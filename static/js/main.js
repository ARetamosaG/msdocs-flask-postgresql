document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const applyFiltersBtn = document.getElementById('apply-filters');
    const resetFiltersBtn = document.getElementById('reset-filters');
    const resultsBody = document.getElementById('results-body');
    const noResultsDiv = document.querySelector('.no-results');
    
    // Cargar datos al iniciar
    loadImageData();
    
    // Eventos de filtros
    applyFiltersBtn.addEventListener('click', loadImageData);
    resetFiltersBtn.addEventListener('click', resetFilters);
    
    function resetFilters() {
        document.getElementById('username').value = '';
        document.getElementById('filename').value = '';
        document.getElementById('date-from').value = '';
        document.getElementById('date-to').value = '';
        document.getElementById('sort-by').value = 'date-desc';
        
        // Recargar datos
        loadImageData();
    }
    
    function loadImageData() {
        // Obtener valores de filtros
        const username = document.getElementById('username').value;
        const filename = document.getElementById('filename').value;
        const dateFrom = document.getElementById('date-from').value;
        const dateTo = document.getElementById('date-to').value;
        const sortBy = document.getElementById('sort-by').value;
        
        // Construir URL con parámetros
        let url = `/api/get-image-data?sort=${sortBy}`;
        if (username) url += `&username=${encodeURIComponent(username)}`;
        if (filename) url += `&filename=${encodeURIComponent(filename)}`;
        if (dateFrom) url += `&date_from=${encodeURIComponent(dateFrom)}`;
        if (dateTo) url += `&date_to=${encodeURIComponent(dateTo)}`;
        
        // Realizar petición AJAX
        fetch(url)
            .then(response => response.json())
            .then(data => {
                displayResults(data);
            })
            .catch(error => {
                console.error('Error al cargar datos:', error);
                resultsBody.innerHTML = '<tr><td colspan="7">Error al cargar datos</td></tr>';
            });
    }
    
    function displayResults(data) {
        resultsBody.innerHTML = ''; // Limpiar tabla
        
        if (data.length === 0) {
            // Mostrar mensaje cuando no hay resultados
            noResultsDiv.style.display = 'block';
            return;
        }
        
        // Ocultar mensaje de no resultados
        noResultsDiv.style.display = 'none';
        
        // Crear filas para cada resultado
        data.forEach(item => {
            const row = document.createElement('tr');
            
            row.innerHTML = `
                <td>${item.processed_date}</td>
                <td>${item.username}</td>
                <td>${item.filename}</td>
                <td>${item.red_pixels}</td>
                <td>${item.green_pixels}</td>
                <td>${item.blue_pixels}</td>
                <td>${item.other_pixels}</td>
            `;
            
            resultsBody.appendChild(row);
        });
    }
});