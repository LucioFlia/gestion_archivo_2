

function updatePagination(filteredRows) {
    const totalPages = Math.ceil(filteredRows.length / rowsPerPage);
    pagination.innerHTML = "";

    for (let i = 1; i <= totalPages; i++) {
        const pageItem = document.createElement("li");
        pageItem.className = "page-item " + (i === currentPage ? "active" : "");
        pageItem.innerHTML = `<a class="page-link" href="javascript:void(0)">${i}</a>`;
        pageItem.addEventListener("click", () => goToPage(i, filteredRows));
        pagination.appendChild(pageItem);
    }
}

function goToPage(page, filteredRows) {
    console.log(rowsPerPage)
    currentPage = page;
    const start = (page - 1) * rowsPerPage;
    const end = start + rowsPerPage;

    rows.forEach(row => (row.style.display = "none")); // Hide all rows
    filteredRows.slice(start, end).forEach(row => (row.style.display = "")); // Show only the rows for the current page

    updatePagination(filteredRows);
}

function filterRows() {
    const filter = document.getElementById(searchInputId).value.toLowerCase();
    const filteredRows = rows.filter(row => row.textContent.toLowerCase().includes(filter));

    currentPage = 1;
    goToPage(1, filteredRows); // Refresh pagination after filtering
}

function sortTable(columnIndex) {
    const isAscending = table.getAttribute("data-sort-dir") === "asc";
    rows.sort((a, b) => {
        const aText = a.cells[columnIndex].textContent.trim();
        const bText = b.cells[columnIndex].textContent.trim();

        if (!isNaN(aText) && !isNaN(bText)) {
            return isAscending ? aText - bText : bText - aText;
        } else {
            return isAscending ?
                aText.localeCompare(bText) :
                bText.localeCompare(aText);
        }
    });

    rows.forEach(row => table.tBodies[0].appendChild(row));

        // Actualizar la dirección de ordenación en el atributo del <table>
        const newSortDir = isAscending ? "desc" : "asc";
        table.setAttribute("data-sort-dir", newSortDir);
    table.setAttribute("data-sort-dir", isAscending ? "desc" : "asc");
      // Actualizar los íconos de las columnas
      const headers = table.querySelectorAll("th");
      headers.forEach((th, index) => {
          const indicator = th.querySelector(".sort-indicator");
          if (indicator) {
              if (index === columnIndex) {
                  // Mostrar icono para la columna ordenada
                  indicator.className = "sort-indicator bi " +
                      (newSortDir === "asc" ? "bi-caret-up-fill" : "bi-caret-down-fill");
              } else {
                  // Resetear iconos para otras columnas
                  indicator.className = "sort-indicator bi";
              }
          }
      });

    filterRows(); // Reapply filtering and pagination after sorting
}

function clearSearch() {
    const searchBox = document.getElementById("searchInputId");
    searchBox.value = "";
    filterRows();
}

//global variables
var searchInputId, tableBodyId, table, pagination, rows, currentSortColumn, currentSortOrder;
// Get the current script tag
const currentScript = document.currentScript;
// Extract the full `src` attribute
const scriptSrc = currentScript.src;
// Use URL and URLSearchParams to parse the query string
const urlParams = new URL(scriptSrc).searchParams;
const rowsPerPage = +urlParams.get('pagination_limit');

function checkTableRecords() {

    const tableBody = document.getElementById('tableBodyId');
    const noRecordsMessage = document.getElementById('noRecordsMessage');
    const pagination = document.getElementById('tableBodyIdPagination');
    

    if (tableBody.children.length === 0) {
        // Mostrar el mensaje "No hay registros" y ocultar la paginación
        noRecordsMessage.style.display = 'block';
        pagination.style.display = 'none';
    } else {
        // Ocultar el mensaje y mostrar la paginación
        noRecordsMessage.style.display = 'none';
        pagination.style.display = 'flex';
    }
}


// Llamar a la función después de cargar los datos en la tabla
if (document.getElementById('noRecordsMessage')){
document.addEventListener('DOMContentLoaded', checkTableRecords);
}



if (document.getElementById('noRecordsMessage')){
document.addEventListener("DOMContentLoaded", function() {
    
    searchInputId = "searchInputId"
    tableBodyId = "tableBodyId";
    table = document.getElementById('tableId');
    pagination = document.getElementById("tableBodyIdPagination");
    rows = Array.from(document.getElementById(tableBodyId).rows);
   
    let currentPage = 1;
    // Initialize filtering, sorting, and pagination
    if (searchInputId) {
        document.getElementById(searchInputId).addEventListener("input", filterRows);
        filterRows(); // Apply initial pagination on page load
    }



    table.addEventListener("click", function (event) {
  
      
    });

});
}

