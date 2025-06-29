// admin_productos.js

document.addEventListener('DOMContentLoaded', function() {
    // Funcionalidad de búsqueda y filtros
    const searchInput = document.getElementById('search-products');
    const filterCategory = document.getElementById('filter-category');
    if (searchInput && filterCategory) {
        searchInput.addEventListener('input', filterProducts);
        filterCategory.addEventListener('change', filterProducts);
    }
    function filterProducts() {
        const searchTerm = searchInput.value.toLowerCase();
        const filterCat = filterCategory.value.toLowerCase();
        const rows = document.querySelectorAll('.product-row');
        rows.forEach(row => {
            const name = row.dataset.name;
            const category = row.dataset.category;
            const matchesSearch = name.includes(searchTerm);
            const matchesFilter = !filterCat || category === filterCat;
            row.style.display = matchesSearch && matchesFilter ? '' : 'none';
        });
    }
    // Funcionalidad de modales
    window.viewProduct = function(productId) {
        window.open(`/producto/${productId}`, '_blank');
    };
    window.deleteProduct = function(productId, productName) {
        document.getElementById('delete-product-name').textContent = productName;
        document.getElementById('delete-modal').classList.remove('hidden');
        document.getElementById('confirm-delete').onclick = function() {
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/admin/producto/eliminar/${productId}`;
            document.body.appendChild(form);
            form.submit();
        };
    };
    window.closeDeleteModal = function() {
        document.getElementById('delete-modal').classList.add('hidden');
    };
    document.getElementById('delete-modal').addEventListener('click', function(e) {
        if (e.target === this) window.closeDeleteModal();
    });
}); 