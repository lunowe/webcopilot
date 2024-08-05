let heading = document.getElementById('heading')
let currentURL = '';

let serverURL = 'https://webcopilot2-k4fym64qpq-ey.a.run.app/'

async function displayTabURL() {
    let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    let url = tab.url;
    // chrome.scripting.executeScript({
    //     target: {tabId: tab.id},
    //     func: () => {
    //         // alert('Current URL: ' + window.location.href);
    //         url = window.location.href;
    //     }
    // });
    currentURL = url;
    heading.innerHTML = url;

    const response = await fetch(`${serverURL}/load_webpage`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({"url": url})
    });
    const data = await response.json();
    alert(data.message);
    const response2 = await fetch(`${serverURL}/summarize`)
    const data2 = await response2.json();
    document.getElementById('output').innerHTML = data2.message;
}

async function sendDataToBackend() {
    alert('Sending data to backend');
    const response = await fetch('http://localhost:8080/summarize')
    const data = await response.json();

    document.getElementById('output').innerHTML = data.message;
}

// document.getElementById('btn').addEventListener('click', sendDataToBackend());

// run displayTabURL() when the popup is opened
displayTabURL();