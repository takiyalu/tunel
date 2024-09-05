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
    document.getElementById('monitorarContainer').style.display = 'block';}
);

document.addEventListener("DOMContentLoaded", function() {
    // Check if there's a success message and scroll to top
    if (document.querySelector('.success-message')) {
        window.scrollTo(0, 0);
    }
});

document.getElementById('monitorarBtn').addEventListener('click', function() {
    var symbol = '{{ ativo_symbol }}';  // Assuming this is passed in the template context
    $.ajax({
        url: '{% url "check_symbol" %}',
        data: {
            'symbol': symbol
        },
        success: function(response) {
            if (response.exists) {
                alert('Ativo already exists in the database.');
            } else {
                // Open the form to create a new Ativo
                document.getElementById('form-section').style.display = 'block';  // Assuming your form is hidden and will be displayed here
            }
        }
    });
});