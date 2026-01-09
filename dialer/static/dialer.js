const phoneInput = document.getElementById('phoneInput');
const addButton = document.getElementById('addButton');
const phoneList = document.getElementById('phoneList');
const newNumbersInput = document.getElementById('newNumbersInput');
const deletedNumbersInput = document.getElementById('deletedNumbersInput');
const deleteButton = document.getElementById('deleteButton');
const campaignCheckboxes = document.querySelectorAll('.campaign-checkbox');
const saveButton = document.getElementById('saveButton');
const ivrSelect = document.getElementById("ivrSelect");
const sipGatewaySelect = document.getElementById("sipGatewaySelect");
const settingsSection = document.getElementById("settingsSection");
const statusSection = document.getElementById("statusSection");
const campaignIvrMenuSelect = document.getElementById('campaignIvrMenuSelect');
const campaignSipGatewaySelect = document.getElementById('campaignSipGatewaySelect');
const concurrentCallsInput = document.getElementById('concurrentCallsInput');
const settingsButton = document.getElementById('settingsButton');
const settingsModal = document.getElementById("settingsModal");
const settingsForm = document.getElementById("settingsForm");
const settingsModalBootstrap = new bootstrap.Modal(settingsModal);
const actionSettingsForm = document.getElementById('actionSettingsForm');
const platformSelect = document.getElementById("platformSelect");
const dbUserInput = document.getElementById("dbUserInput");
const dbPasswordInput = document.getElementById("dbPasswordInput");
const dbHostInput = document.getElementById("dbHostInput");
const dbPortInput = document.getElementById("dbPortInput");
const eslConfig = document.getElementById("eslConfig");
const eslIp = document.getElementById("eslIp");
const eslPort = document.getElementById("eslPort");
const eslSecret = document.getElementById("eslSecret");
let leadsInCampaign = [];
let newNumbers = [];
let deletedNumbers = [];

actionSettingsForm.value = "d4dialer_settings_save";

settingsForm.addEventListener('submit', function(event){
    console.log("submit");
});

settingsButton.addEventListener('click', function(){
    platformSelect.value = voipPlatform;
    settingsModalBootstrap.show();

    const csrftoken = document.getElementById("csrf-token").value;
    const formData = new FormData(); 
    formData.append("action", "d4dialer_settings_platform_config_query"); 

    fetch(dialerUrl, {
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
        platformSelect.value = data.voip_platform_database.voip_platform;
        dbUserInput.value = data.voip_platform_database.voip_platform_db_user;
        dbPasswordInput.value = data.voip_platform_database.voip_platform_db_password;
        dbHostInput.value = data.voip_platform_database.voip_platform_db_host;
        dbPortInput.value = data.voip_platform_database.voip_platform_db_port;

        if (platformSelect.value == 'fusionpbx' || platformSelect.value == 'freeswitch'){
            eslConfig.style.display = "block";
            eslIp.value = data.voip_platform_api.voip_platform_api_host;
            eslPort.value = data.voip_platform_api.voip_platform_api_port;
            eslSecret.value = data.voip_platform_api.voip_platform_api_password;
        } else {
            eslConfig.style.display = "none";
        }
    })
    .catch(error => {
        console.error("Error fetching leads:", error);
    });
});

platformSelect.addEventListener("change", function() {
    const csrftoken = document.getElementById("csrf-token").value;
    const formData = new FormData(); 
    formData.append("action", "d4dialer_settings_platform_config_default_query"); 
    formData.append("voip_platform", platformSelect.value);    

    fetch(dialerUrl, {
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
        dbUserInput.value = data.voip_platform_database.USER;
        dbPasswordInput.value = data.voip_platform_database.PASSWORD;
        dbHostInput.value = data.voip_platform_database.HOST;
        dbPortInput.value = data.voip_platform_database.PORT;

        if (platformSelect.value == 'fusionpbx' || platformSelect.value == 'freeswitch'){
            eslConfig.style.display = "block";
            eslIp.value = data.voip_platform_api.IP;
            eslPort.value = data.voip_platform_api.PORT;
            eslSecret.value = data.voip_platform_api.SECRET;
        } else {
            eslConfig.style.display = "none";
        }
    })
    .catch(error => {
        console.error("Error fetching leads:", error);
    });            
});

document.getElementById('d4dialerTitle').addEventListener('click', function() {
    window.location.href = dialerUrl;
});   

if (dbConnection && apiConnection){
    saveButton.style.display = 'none';
    deleteButton.style.display = 'none';
    settingsSection.style.display = 'none';
    statusSection.style.display = 'none'; 

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
        form.action = dialerUrl;

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
} else if (!dbConnection) {
console.log("No DB connection");  
} else if(!apiConnection) {
    console.log("No API connection");  
} else {
console.log("Internal Error"); 
}