<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold">Family Groups </h1>
      <button
        @click="showCreateModal = true"
        class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
      >
        Create Group
      </button>
    </div>

    <!-- Groups Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="group in groups"
        :key="group.id"
        class="bg-white rounded-lg shadow-md overflow-hidden"
      >
        <div class="p-4">
          <div class="flex justify-between items-start mb-4">
            <div>
              <h3 class="text-xl font-semibold mb-2">{{ group.name }}</h3>
              <p class="text-gray-600">{{ group.description }}</p>
            </div>
            <button
              v-if="canDeleteGroup(group)"
              @click="confirmDelete(group)"
              class="text-red-600 hover:text-red-800"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
          
          <!-- Members Section -->
          <div class="mt-4">
            <h4 class="font-medium text-gray-700 mb-2">Members</h4>
            <ul class="space-y-2">
              <li
                v-for="member in groupMembers[group.id]"
                :key="member.id"
                class="flex justify-between items-center"
              >
                <span>{{ member.name }}</span>
                <button
                  @click="removeMember(group.id, member.id)"
                  class="text-red-600 hover:text-red-800 text-sm"
                >
                  Remove
                </button>
              </li>
            </ul>
            
            <!-- Add Member Form -->
            <div class="mt-4">
              <div class="flex space-x-2">
                <input
                  v-model="newMemberEmails[group.id]"
                  type="email"
                  placeholder="Enter email"
                  class="flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
                <button
                  @click="addMember(group.id)"
                  class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                >
                  Add
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Group Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="text-2xl font-bold mb-4">Create Family Group</h2>
        
        <form @submit.prevent="handleCreateGroup" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">Name</label>
            <input
              v-model="form.name"
              type="text"
              required
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700">Description</label>
            <textarea
              v-model="form.description"
              required
              rows="3"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            ></textarea>
          </div>
          
          <div class="flex justify-end space-x-3">
            <button
              type="button"
              @click="showCreateModal = false"
              class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Create
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="text-2xl font-bold mb-4">Delete Group</h2>
        <p class="text-gray-600 mb-6">
          Are you sure you want to delete "{{ selectedGroup?.name }}"? This action cannot be undone.
        </p>
        <div class="flex justify-end space-x-3">
          <button
            @click="showDeleteModal = false"
            class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            @click="deleteGroup"
            class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { groups as groupsApi } from '@/services/api';
import { useToast } from 'vue-toast-notification';
import { useAuthStore } from '@/stores/auth';

const groups = ref([]);
const groupMembers = ref({});
const newMemberEmails = ref({});
const showCreateModal = ref(false);
const showDeleteModal = ref(false);
const selectedGroup = ref(null);
const toast = useToast();
const authStore = useAuthStore();

const form = ref({
  name: '',
  description: '',
});

const fetchGroups = async () => {
  try {
    const response = await groupsApi.getAll();
    groups.value = response.data;
    // Fetch members for each group
    groups.value.forEach(group => {
      fetchGroupMembers(group.id);
      newMemberEmails.value[group.id] = '';
    });
  } catch (error) {
    toast.error('Failed to fetch groups');
  }
};

const fetchGroupMembers = async (groupId) => {
  try {
    const response = await groupsApi.getMembers(groupId);
    groupMembers.value[groupId] = response.data;
  } catch (error) {
    toast.error(`Failed to fetch members for group`);
  }
};

const handleCreateGroup = async () => {
  try {
    await groupsApi.create(form.value);
    toast.success('Group created successfully');
    await fetchGroups();
    showCreateModal.value = false;
    form.value = { name: '', description: '' };
  } catch (error) {
    toast.error('Failed to create group');
  }
};

const canDeleteGroup = (group) => {
  const userData = authStore.user?.user_metadata;
  const userId = authStore.user?.id;
  
  console.log('Auth Store State:', {
    user: authStore.user,
    metadata: userData,
    userId: userId,
    groupOwnerId: group.owner_id
  });
  
  return group.owner_id === userId || 
         (userData?.role && ['admin', 'super_admin'].includes(userData.role.toLowerCase()));
};

const confirmDelete = (group) => {
  selectedGroup.value = group;
  showDeleteModal.value = true;
};

const deleteGroup = async () => {
  try {
    await groupsApi.delete(selectedGroup.value.id);
    toast.success('Group deleted successfully');
    await fetchGroups();
    showDeleteModal.value = false;
  } catch (error) {
    toast.error('Failed to delete group');
  }
};

const addMember = async (groupId) => {
  try {
    const email = newMemberEmails.value[groupId];
    if (!email) return;
    
    await groupsApi.addMember(groupId, email);
    toast.success('Member added successfully');
    await fetchGroupMembers(groupId);
    newMemberEmails.value[groupId] = '';
  } catch (error) {
    toast.error('Failed to add member');
  }
};

const removeMember = async (groupId, userId) => {
  try {
    await groupsApi.removeMember(groupId, userId);
    toast.success('Member removed successfully');
    await fetchGroupMembers(groupId);
  } catch (error) {
    toast.error('Failed to remove member');
  }
};

onMounted(() => {
  fetchGroups();
});
</script> 