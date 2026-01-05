const phoneInput = document.getElementById('phoneInput');
const addButton = document.getElementById('addButton');
const phoneList = document.getElementById('phoneList');
const newNumbersInput = document.getElementById('newNumbersInput');
const deletedNumbersInput = document.getElementById('deletedNumbersInput');
const campaignUuidInput = document.getElementById('campaignUuidInput');      
const dialerForm = document.getElementById('dialerForm');
const deleteButton = document.getElementById('deleteButton');
const campaignCheckboxes = document.querySelectorAll('.campaign-checkbox');
const saveButton = document.getElementById('saveButton');
const ivrSelect = document.getElementById("ivrSelect");
const sipGatewaySelect = document.getElementById("sipGatewaySelect");
const settingsSection = document.getElementById("settingsSection");
const statusSection = document.getElementById("statusSection");
const campaignIvrMenuSelect = document.getElementById('campaignIvrMenuSelect');
const campaignSipGatewaySelect = document.getElementById('campaignSipGatewaySelect');
const campaignUuidInputStart = document.getElementById('campaignUuidInputStart');
const concurrentCallsInput = document.getElementById('concurrentCallsInput');
const campaignStatusP = document.getElementById('campaignStatusP');
const PAGE_SIZE = 10;
let currentPage = 1;
let leadsInCampaign = [];
let newNumbers = [];
let selectedCampaignUuid = "";
let deletedNumbers = [];

saveButton.style.display = 'none';
deleteButton.style.display = 'none';
settingsSection.style.display = 'none';
statusSection.style.display = 'none';


document.getElementById('d4dialerTitle').addEventListener('click', function() {
window.location.href = "{% url 'dialer' %}";
});

deleteButton.addEventListener('click', function() {
// Get all checked checkboxes
const checked = Array.from(document.querySelectorAll('.campaign-checkbox:checked'));
if (checked.length === 0) {
    alert('Please select at least one campaign to delete.');
    return;
}
if (!confirm('Are you sure you want to delete the selected campaign(s)?')) {
    return;
}

// Collect campaign IDs to delete
const campaignIds = checked.map(cb => cb.getAttribute('data-campaign-id'));

// Create a form and submit it to Django for deletion
const form = document.createElement('form');
form.method = 'post';
form.action = '{% url "dialer" %}';

// Add CSRF token
const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
const csrfInput = document.createElement('input');
csrfInput.type = 'hidden';
csrfInput.name = 'csrfmiddlewaretoken';
csrfInput.value = csrfToken;
form.appendChild(csrfInput);

// Add action
const actionInput = document.createElement('input');
actionInput.type = 'hidden';
actionInput.name = 'action';
actionInput.value = 'delete';
form.appendChild(actionInput);

// Add campaign IDs
campaignIds.forEach(id => {
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'campaign_ids';
    input.value = id;
    form.appendChild(input);
});

document.body.appendChild(form);
form.submit();
});

campaignCheckboxes.forEach(checkbox => {
checkbox.addEventListener('change', function() {
    const anyChecked = Array.from(campaignCheckboxes).some(cb => cb.checked);
    deleteButton.style.display = anyChecked ? 'inline-block' : 'none';
});
});

addButton.addEventListener('click', function() {
const value = phoneInput.value.trim();
if (value) {
    newNumbers.push(value);
    let noDuplicateNewNumbers = [...new Set(newNumbers)];
    newNumbersInput.value = JSON.stringify(noDuplicateNewNumbers);
    phoneInput.value = '';
    phoneInput.focus();
    settingsSection.style.display = 'block';
    saveButton.style.display = 'block';

    const phoneList = document.getElementById("phoneList");
    phoneList.innerHTML = "";
    newNumbers.forEach(number => {
    appendPhoneToPhoneList({phone_number: number}, phoneList);
    });

    leadsInCampaign.forEach(lead => {
    appendPhoneToPhoneList(lead, phoneList);
    });

    deletedNumbers.forEach((number, index) => {
    if (number === value) {              
        deletedNumbers.splice(index, 1);
        deletedNumbersInput.value = JSON.stringify(deletedNumbers);
    }
    });
}
});          

document.querySelectorAll('.campaign-item').forEach(item => {
item.addEventListener('click', function() {
    const campaignId = this.getAttribute('data-campaign-id');
    const selectedCampaignUuiDiv = document.getElementById('selectedCampaignUuid');
    selectedCampaignUuiDiv.textContent = '';
    newNumbers = [];
    deletedNumbers = [];
    {% for campaign in campaigns %}
    if (campaignId == "{{ campaign.id }}") {
        selectedCampaignUuiDiv.textContent = "{{ campaign.campaign_uuid }}";
        selectedCampaignUuid = "{{ campaign.campaign_uuid }}";
        campaignUuidInput.value = "{{ campaign.campaign_uuid }}";
        campaignUuidInputStart.value = "{{ campaign.campaign_uuid }}";
        ivrSelect.value = "{{ campaign.campaign_ivr_menu }}";              
        campaignIvrMenuSelect.value = "{{ campaign.campaign_ivr_menu }}";
        sipGatewaySelect.value = "{{ campaign.campaign_sip_gateway }}";
        campaignSipGatewaySelect.value = "{{ campaign.campaign_sip_gateway }}";
        settingsSection.style.display = 'block';
        statusSection.style.display = 'block';
        saveButton.style.display = 'none';
        concurrentCallsInput.value = "{{ campaign.campaign_concurrent_calls }}";
        campaignConcurrentCallsInput.value = "{{ campaign.campaign_concurrent_calls }}";    
        
        const csrftoken = document.getElementById("csrf-token").value;
        const formData = new FormData(); 
        formData.append("action", "campaign_query"); 
        formData.append("campaign_uuid_query", selectedCampaignUuid);

        fetch("{% url 'dialer' %}", {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken 
        },
        body: formData
        })
        .then(response => {
            if (!response.ok) {
            throw new Error(response.status);
            }
            return response.json();
        })
        .then(data => {
            const phoneList = document.getElementById("phoneList");
            phoneList.innerHTML = "";
            leadsInCampaign = [];

            data.leads.forEach(lead => {                    
            leadsInCampaign.push(lead);
            appendPhoneToPhoneList(lead, phoneList);
            });

            campaignStatusP.innerText = data.campaign_status;
            if (data.campaign_status == 'COMPLETED') {
            startButton.disabled = true;
            } else {
            startButton.disabled = false;
            }
        })
        .catch(error => {
            console.error("Error fetching leads:", error);
        });
    }
    {% endfor %}
});
});      

ivrSelect.addEventListener("change", function() {
const selectedValue = ivrSelect.value;
campaignIvrMenuSelect.value = selectedValue;
saveButton.style.display = 'inline-block';
});

sipGatewaySelect.addEventListener("change", function() {
const selectedValue = sipGatewaySelect.value;
campaignSipGatewaySelect.value = selectedValue;
saveButton.style.display = 'inline-block';
});

concurrentCallsInput.addEventListener("input", function() {
const concurrentValue = concurrentCallsInput.value;
campaignConcurrentCallsInput.value = concurrentValue;
saveButton.style.display = 'inline-block';
});

appendPhoneToPhoneList = function(lead,list) {
const li = document.createElement("li");
li.className = "list-group-item d-flex justify-content-between";

const phoneSpan = document.createElement("span");
phoneSpan.textContent = lead.phone_number;

const statusSpan = document.createElement("span");
statusSpan.textContent = lead.status || "N/A";

const deleteBtn = document.createElement("button");
deleteBtn.className = "btn btn-sm btn-outline-danger";
deleteBtn.innerHTML = '<i class="bi bi-trash"></i>';

deleteBtn.addEventListener("click", () => { 
    deletedNumbers.push(lead.phone_number);
    deletedNumbersInput.value = JSON.stringify(deletedNumbers);   
    newNumbers.forEach((number, index) => {
    if (number === lead.phone_number) {
        newNumbers.splice(index, 1);
        newNumbersInput.value = JSON.stringify(newNumbers);
    }
    });       
    li.remove();
    saveButton.style.display = 'block';
});

li.appendChild(phoneSpan);
li.appendChild(statusSpan);
li.appendChild(deleteBtn);
list.appendChild(li);
};