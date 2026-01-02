from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import connections

from freeswitchESL import ESL

class FusionpbxApiHandler(APIView):
	def post(self, request):
		try:
			data = request.data
			token = data.get("token")
			action = data.get("action")
			endpoint = data.get("endpoint")
			destination = data.get("destination")
			domain = data.get("domain")
		
			cursor = connections['fusionpbx'].cursor()
			cursor.execute("select api_key from v_users;")
			rows = cursor.fetchall()
			api_keys = [r[0] for r in rows]

			if not token in api_keys:
				return Response({"reason": "ACCESS_DENIED"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

			if action == "originate":
				cursor.execute("select extension from v_extensions;")
				rows = cursor.fetchall()
				extensions = [r[0] for r in rows]

				if endpoint in extensions:
					endpoint_url = f"user/{endpoint}@{domain}"
				else:
					endpoint_url = f"sofia/gateway/db0a2ab6-1243-425d-846e-c76e5ca8a961/{endpoint}"
		
				if destination in extensions:
					destination_url = destination
				else:
					#Logic to call any ivr even when IVR Direct dial is False
					#application $ivr is used instead of a dialplan extension				

					cursor.execute("select ivr_menu_extension,ivr_menu_uuid from v_ivr_menus;")
					rows = cursor.fetchall()
					
					map = {ext: uuid for ext, uuid in rows}
					ivr_menu_uuid = map.get(destination)

					if ivr_menu_uuid:
						destination_url = f"&ivr({ivr_menu_uuid})"
					else:
						return Response({"reason": "FAILED"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

				cmd = f"originate {{ignore_early_media=true}}{endpoint_url} {destination_url}"

				esl_conn = ESL.ESLconnection("127.0.0.1", "8021", "ClueCon")
				if not esl_conn.connected():
					return Response({"reason": "FAILED"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
				response = esl_conn.bgapi(cmd)
				job_uuid_response = response.getHeader("Job-UUID")	
				esl_conn.events("plain","BACKGROUND_JOB CHANNEL_CALLSTATE")
				unique_id = ""
				while esl_conn.connected():
					events = esl_conn.recvEvent()
					if events.getHeader("Event-Name") == "BACKGROUND_JOB":
						if events.getHeader("Job-UUID") == job_uuid_response:
							if events.getBody().split(" ")[0].strip() == "+OK":
								unique_id = events.getBody().split(" ")[1].strip()
							if events.getBody().split(" ")[0].strip() == "-ERR":
								hangup_cause = events.getBody().split(" ")[1].strip()
								break
					if unique_id:
						if events.getHeader("Unique-ID") == unique_id:
							if events.getHeader("Channel-Call-State") == "HANGUP":
								hangup_cause = events.getHeader("Hangup-Cause")
								break
								
				esl_conn.disconnect()		
				return Response({"reason": f"{hangup_cause}"})
			else:
				return Response({"reason": "NOT_IMPLEMENTED"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		except Exception as e:
			return Response({"reason": "FAILED"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
