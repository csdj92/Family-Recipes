<template>
  <div class="groups-container">
    <h2>My Family Groups </h2>
    <div class="groups-list">
      <div v-for="group in groups" :key="group.id" class="group-card">
        <div class="group-info">
          <h3>{{ group.name }}</h3>
          <p>Created: {{ formatDate(group.created_at) }}</p>
        </div>
        <div class="group-actions">
          <button @click="viewGroup(group)" class="btn btn-primary">View</button>
          <button 
            v-if="canDeleteGroup(group)" 
            @click="confirmDelete(group)" 
            class="btn btn-danger ml-2"
          >
            Delete
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Delete Group</h3>
        <p>Are you sure you want to delete "{{ selectedGroup?.name }}"? This action cannot be undone.</p>
        <div class="modal-actions">
          <button @click="deleteGroup" class="btn btn-danger">Delete</button>
          <button @click="showDeleteModal = false" class="btn btn-secondary">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import axios from 'axios';

export default {
  name: 'GroupList',
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();
    const groups = ref([]);
    const showDeleteModal = ref(false);
    const selectedGroup = ref(null);

    const fetchGroups = async () => {
      try {
        const response = await axios.get('/api/groups', {
          headers: {
            Authorization: `Bearer ${authStore.token}`
          }
        });
        groups.value = response.data;
        console.log('Auth Store State:', {
          userRole: authStore.userRole,
          userId: authStore.userId,
          token: authStore.token ? 'Present' : 'Missing'
        });
        console.log('Fetched Groups:', groups.value);
      } catch (error) {
        console.error('Error fetching groups:', error);
      }
    };

    const viewGroup = (group) => {
      router.push(`/groups/${group.id}`);
    };

    const canDeleteGroup = (group) => {
      console.log('User Role:', authStore.userRole);
      console.log('User ID:', authStore.userId);
      console.log('Group Owner ID:', group.owner_id);
      console.log('Can Delete?:', group.owner_id === authStore.userId || 
                 ['admin', 'super_admin'].includes(authStore.userRole?.toLowerCase()));
      return group.owner_id === authStore.userId || 
             ['admin', 'super_admin'].includes(authStore.userRole?.toLowerCase());
    };

    const confirmDelete = (group) => {
      selectedGroup.value = group;
      showDeleteModal.value = true;
    };

    const deleteGroup = async () => {
      try {
        await axios.delete(`/api/groups/${selectedGroup.value.id}`, {
          headers: {
            Authorization: `Bearer ${authStore.token}`
          }
        });
        await fetchGroups(); // Refresh the list
        showDeleteModal.value = false;
      } catch (error) {
        console.error('Error deleting group:', error);
      }
    };

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString();
    };

    onMounted(() => {
      console.log('Component Mounted - Auth Store State:', {
        userRole: authStore.userRole,
        userId: authStore.userId,
        token: authStore.token ? 'Present' : 'Missing'
      });
      fetchGroups();
    });

    return {
      groups,
      viewGroup,
      canDeleteGroup,
      confirmDelete,
      deleteGroup,
      showDeleteModal,
      selectedGroup,
      formatDate
    };
  }
};
</script>

<style scoped>
.groups-container {
  padding: 20px;
}

.groups-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.group-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.group-info h3 {
  margin: 0 0 8px 0;
  color: #333;
}

.group-info p {
  margin: 0;
  color: #666;
  font-size: 0.9em;
}

.group-actions {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-weight: 500;
}

.btn-primary {
  background-color: #4CAF50;
  color: white;
}

.btn-danger {
  background-color: #f44336;
  color: white;
}

.btn-secondary {
  background-color: #9e9e9e;
  color: white;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 24px;
  border-radius: 8px;
  width: 90%;
  max-width: 400px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}

.ml-2 {
  margin-left: 8px;
}
</style> 