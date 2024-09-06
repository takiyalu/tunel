function validateForm() {
    const nameInput = document.getElementById('nome').value.trim();
    const tickerInput = document.getElementById('ticker').value.trim();

    if (nameInput === "" && tickerInput === "") {
        // Previne o usário de preencher ambos os campos vazios(Buscam todos os ativos existentes)
        alert("Ao menos um dos campos deve ser preenchido");
        return false;
    }
    return true;
}

document.getElementById('monitorarBtn').addEventListener('click', function() {
    const ticker = document.getElementById('ticker').value.trim(); // Get the ticker value

    if (ticker) { // Ensure ticker is not empty
        validateProduct(ticker);
    } else {
        alert("Ticker cannot be empty.");
    }
});

document.addEventListener("DOMContentLoaded", function() {
    // Check if there's a success message and scroll to top
    if (document.querySelector('.success-message')) {
        window.scrollTo(0, 0);
    }
});

function validateProduct(ticker) {
    // Send an AJAX request to the server to check if the product is already monitored
    fetch(`/ativo/?ticker=${ticker}`, {  // Ensure URL is correct
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())  // Convert response to JSON
    .then(data => {
        const modal = new bootstrap.Modal(document.getElementById('error-modal'));
        const messageElement = document.getElementById('error-message');
        const closeButton = document.querySelector('.close-btn');

        if (data.is_monitored) {
            messageElement.innerText = "This product is already being monitored.";
            modal.show();
            document.getElementById('monitorarContainer').style.display = 'none'; // Hide the monitorarContainer
        } else {
            messageElement.innerText = "";
            modal.hide();
            document.getElementById('monitorarContainer').style.display = 'block'; // Show the monitorarContainer
        }
    })
    .catch(error => console.error('Error:', error));
}
