// Configuración global
let currentPage = 1;
let perPage = 10;
let totalPages = 1;
let currentFilters = {
    username: '',
    filename: '',
    dateFrom: '',
    dateTo: '',
    sortBy: 'date-desc'
};

// Función que se ejecuta cuando la página ha cargado
document.addEventListener('DOMContentLoaded', function() {
    // Cargar datos iniciales
    loadData();
    
    // Configurar botones de filtro
    document.getElementById('apply-filters').addEventListener('click', applyFilters);
    document.getElementById('reset-filters').addEventListener('click', resetFilters);
    
    // Configurar paginación
    document.getElementById('prev-page').addEventListener('click', prevPage);
    document.getElementById('next-page').addEventListener('click', nextPage);
    
    // Configurar ordenamiento por columnas
    document.querySelectorAll('th[data-sort]').forEach(header => {
        header.addEventListener('click', function() {
            const sortField = this.getAttribute('data-sort');
            sortBy(sortField);
        });
    });
});

// Función para cargar datos del servidor
function loadData() {
    // Construir URL con parámetros
    const params = new URLSearchParams({
        username: currentFilters.username,
        filename: currentFilters.filename,
        date_from: currentFilters.dateFrom,
        date_to: currentFilters.dateTo,
        sort_by: currentFilters.sortBy,
        page: currentPage,
        per_page: perPage
    });
    
    // Hacer solicitud al servidor
    fetch(`/api/get-image-data?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayData(data.data);
                updatePagination(data.pagination);
            } else {
                showError('Error cargando datos');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('Error de conexión con el servidor');
        });
}

// Función para mostrar datos en la tabla
function displayData(items) {
    const tableBody = document.getElementById('results-body');
    const noResults = document.querySelector('.no-results');
    
    // Limpiar tabla actual
    tableBody.innerHTML = '';
    
    if (items.length === 0) {
        // Mostrar mensaje de no resultados
        noResults.style.display = 'block';
        return;
    }
    
    // Ocultar mensaje si hay resultados
    noResults.style.display = 'none';
    
    // Crear filas para cada elemento
    items.forEach(item => {
        const row = document.createElement('tr');
        
        // Crear celdas con los datos
        row.innerHTML = `
            <td>${item.processed_date}</td>
            <td>${item.username}</td>
            <td>${item.filename}</td>
            <td>${item.red_pixels.toLocaleString()}</td>
            <td>${item.green_pixels.toLocaleString()}</td>
            <td>${item.blue_pixels.toLocaleString()}</td>
            <td>${item.other_pixels.toLocaleString()}</td>
        `;
        
        tableBody.appendChild(row);
    });
}

// Función para actualizar controles de paginación
function updatePagination(pagination) {
    const paginationDiv = document.querySelector('.pagination');
    
    // Actualizar variables globales
    currentPage = pagination.current_page;
    totalPages = pagination.total_pages;
    
    // Limpiar botones de página existentes, mantener solo Anterior y Siguiente
    const prevButton = document.getElementById('prev-page');
    const nextButton = document.getElementById('next-page');
    
    // Eliminar botones de números de página existentes
    Array.from(paginationDiv.querySelectorAll('button:not(#prev-page):not(#next-page)')).forEach(btn => {
        paginationDiv.removeChild(btn);
    });
    
    // Crear nuevos botones de página
    for (let i = Math.max(1, currentPage - 2); i <= Math.min(totalPages, currentPage + 2); i++) {
        const button = document.createElement('button');
        button.textContent = i;
        if (i === currentPage) {
            button.classList.add('current-page');
        }
        
        button.addEventListener('click', function() {
            if (currentPage !== i) {
                currentPage = i;
                loadData();
            }
        });
        
        // Insertar antes del botón Siguiente
        paginationDiv.insertBefore(button, nextButton);
    }
    
    // Activar/desactivar botones Anterior/Siguiente
    prevButton.disabled = currentPage <= 1;
    nextButton.disabled = currentPage >= totalPages;
}

// Función para aplicar filtros
function applyFilters() {
    currentFilters = {
        username: document.getElementById('username').value.trim(),
        filename: document.getElementById('filename').value.trim(),
        dateFrom: document.getElementById('date-from').value,
        dateTo: document.getElementById('date-to').value,
        sortBy: document.getElementById('sort-by').value
    };
    
    // Reiniciar a la primera página al filtrar
    currentPage = 1;
    loadData();
}

// Función para resetear filtros
function resetFilters() {
    // Limpiar campos de filtro
    document.getElementById('username').value = '';
    document.getElementById('filename').value = '';
    document.getElementById('date-from').value = '';
    document.getElementById('date-to').value = '';
    document.getElementById('sort-by').value = 'date-desc';
    
    // Resetear filtros en la variable global
    currentFilters = {
        username: '',
        filename: '',
        dateFrom: '',
        dateTo: '',
        sortBy: 'date-desc'
    };
    
    // Volver a la primera página
    currentPage = 1;
    loadData();
}

// Funciones de paginación
function prevPage() {
    if (currentPage > 1) {
        currentPage--;
        loadData();
    }
}

function nextPage() {
    if (currentPage < totalPages) {
        currentPage++;
        loadData();
    }
}

// Función para ordenar por una columna
function sortBy(field) {
    // Alternar entre ascendente y descendente
    if (currentFilters.sortBy === field) {
        if (field === 'date') {
            currentFilters.sortBy = currentFilters.sortBy === 'date-desc' ? 'date-asc' : 'date-desc';
        } else {
            // Para otros campos, alternar entre campo y campo-desc
            currentFilters.sortBy = currentFilters.sortBy.includes('-desc') ? field : `${field}-desc`;
        }
    } else {
        // Por defecto ordenar descendente
        currentFilters.sortBy = field;
    }
    
    // Actualizar select para reflejar el cambio
    const sortSelect = document.getElementById('sort-by');
    sortSelect.value = currentFilters.sortBy;
    
    // Volver a cargar con el nuevo orden
    loadData();
}

// Función para mostrar errores
function showError(message) {
    const tableBody = document.getElementById('results-body');
    const noResults = document.querySelector('.no-results');
    
    // Limpiar tabla y mostrar mensaje
    tableBody.innerHTML = '';
    noResults.textContent = message;
    noResults.style.display = 'block';
}