document.addEventListener('DOMContentLoaded', function() {
    console.log("VettoreFlow UI carregada!");

    // Sistema de ordenação de tabelas
    const getCellValue = (tr, idx) => tr.children[idx].innerText || tr.children[idx].textContent;

    const comparer = (idx, asc) => (a, b) => ((v1, v2) => 
        v1 !== '' && v2 !== '' && !isNaN(v1) && !isNaN(v2) ? v1 - v2 : v1.toString().localeCompare(v2)
    )(getCellValue(asc ? a : b, idx), getCellValue(asc ? b : a, idx));

    document.querySelectorAll('th.sortable').forEach(th => th.addEventListener('click', (() => {
        const table = th.closest('table');
        const tbody = table.querySelector('tbody');
        
        // Alternar direção
        const currentAsc = th.classList.contains('sort-asc');
        
        // Limpar outras colunas
        table.querySelectorAll('th').forEach(header => {
            header.classList.remove('sort-asc', 'sort-desc');
        });

        // Aplicar nova direção
        if (currentAsc) {
            th.classList.add('sort-desc');
        } else {
            th.classList.add('sort-asc');
        }

        Array.from(tbody.querySelectorAll('tr'))
            .sort(comparer(Array.from(th.parentNode.children).indexOf(th), !currentAsc))
            .forEach(tr => tbody.appendChild(tr));
    })));
});
