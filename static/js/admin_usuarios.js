// admin_usuarios.js

document.addEventListener('DOMContentLoaded', function() {
    // Funcionalidad de búsqueda y filtros
    const searchInput = document.getElementById('search-users');
    const filterType = document.getElementById('filter-type');
    if (searchInput && filterType) {
        searchInput.addEventListener('input', filterUsers);
        filterType.addEventListener('change', filterUsers);
    }
    function filterUsers() {
        const searchTerm = searchInput.value.toLowerCase();
        const filterT = filterType.value;
        const rows = document.querySelectorAll('.user-row');
        rows.forEach(row => {
            const name = row.dataset.name;
            const email = row.dataset.email;
            const type = row.dataset.type;
            const matchesSearch = name.includes(searchTerm) || email.includes(searchTerm);
            const matchesFilter = !filterT || type === filterT;
            row.style.display = matchesSearch && matchesFilter ? '' : 'none';
        });
    }
    // Funcionalidad de ordenamiento
    window.sortTable = function(columnIndex) {
        const table = document.getElementById('users-table-body');
        const rows = Array.from(table.querySelectorAll('tr'));
        rows.sort((a, b) => {
            const aValue = a.cells[columnIndex].textContent.trim().toLowerCase();
            const bValue = b.cells[columnIndex].textContent.trim().toLowerCase();
            return aValue.localeCompare(bValue);
        });
        rows.forEach(row => table.appendChild(row));
    };
    // Funcionalidad de modales
    window.viewUser = function(userId) {
        document.getElementById('user-modal').classList.remove('hidden');
    };
    window.editUser = function(userId) {
        window.location.href = `/admin/usuario/editar/${userId}`;
    };
    window.deleteUser = function(userId, userName) {
        document.getElementById('delete-user-name').textContent = userName;
        document.getElementById('delete-modal').classList.remove('hidden');
        document.getElementById('confirm-delete').onclick = function() {
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/admin/usuario/eliminar/${userId}`;
            document.body.appendChild(form);
            form.submit();
        };
    };
    window.closeUserModal = function() {
        document.getElementById('user-modal').classList.add('hidden');
    };
    window.closeDeleteModal = function() {
        document.getElementById('delete-modal').classList.add('hidden');
    };
    document.getElementById('user-modal').addEventListener('click', function(e) {
        if (e.target === this) window.closeUserModal();
    });
    document.getElementById('delete-modal').addEventListener('click', function(e) {
        if (e.target === this) window.closeDeleteModal();
    });
}); 