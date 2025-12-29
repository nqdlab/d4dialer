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
				return Response("ACCESS_DENIED")

			if action == "originate":
				cursor.execute("select extension from v_extensions;")
				rows = cursor.fetchall()
				extensions = [r[0] for r in rows]
		
				if destination in extensions:
					cmd = f"originate {{ignore_early_media=true}}user/{endpoint}@{domain} {destination}"
				else:
					#Logic to call any ivr even when IVR Direct dial is False
					#application $ivr is used instead of a dialplan extension				

					cursor.execute("select ivr_menu_extension,ivr_menu_uuid from v_ivr_menus;")
					rows = cursor.fetchall()
					
					map = {ext: uuid for ext, uuid in rows}
					ivr_menu_uuid = map.get(destination)

					if ivr_menu_uuid:
						cmd = f"originate {{ignore_early_media=true}}user/{endpoint}@{domain} &ivr({ivr_menu_uuid})"
					else:
						return Response("FAILED")

				esl_conn = ESL.ESLconnection("127.0.0.1", "8021", "ClueCon")
				if not esl_conn.connected():
					return Response("FAILED")				
				response = esl_conn.bgapi(cmd)
				job_uuid_reponse = response.getHeader("Job-UUID")	
				esl_conn.events("plain","BACKGROUND_JOB CHANNEL_CALLSTATE")
				unique_id = ""
				while esl_conn.connected():
					events = esl_conn.recvEvent()
					if events.getHeader("Event-Name") == "BACKGROUND_JOB":						
						if events.getHeader("Job-UUID") == job_uuid_reponse:
							unique_id = events.getBody().split(" ")[1].strip()
					if unique_id:
						if events.getHeader("Channel-Call-State") == "HANGUP":
							if events.getHeader("Unique-ID") == unique_id:
								break
								
				esl_conn.disconnect()		
				return Response("COMPLETED")
			else:
				return Response("NOT_IMPLEMENTED")
		except Exception as e:
			return Response("FAILED")
