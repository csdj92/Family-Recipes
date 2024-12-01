<template>
  <div class="min-h-screen bg-gray-100">
    <div class="container mx-auto p-6">
      <!-- Navigation -->
      <div class="mb-6 flex items-center space-x-4">
        <router-link to="/" class="flex items-center text-sm text-gray-600 hover:text-gray-900">
          <ChevronLeft class="mr-1 h-4 w-4" />
          Back
        </router-link>
        <div class="h-4 w-px bg-gray-300"></div>
        <router-link to="/" class="text-sm text-gray-600 hover:text-gray-900">
          Recipe Sharing
        </router-link>
      </div>

      <!-- Recipe Grid -->
      <div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div v-for="recipe in recipes" :key="recipe.id" class="bg-white rounded-lg shadow-md overflow-hidden">
          <img
            v-if="recipe.image_url"
            :src="recipe.image_url"
            :alt="recipe.title"
            class="h-48 w-full object-cover"
          />
          
          <div class="p-6">
            <h2 class="text-2xl font-bold mb-2">{{ recipe.title }}</h2>
            <p v-if="recipe.description" class="text-sm text-gray-600 mb-4">
              {{ recipe.description }}
            </p>
            
            <!-- Ingredients Section -->
            <div class="mb-6">
              <h3 class="font-semibold mb-3">Ingredients</h3>
              <ul class="list-disc list-inside space-y-2 text-sm">
                <li v-for="(amount, ingredient) in recipe.ingredients" :key="ingredient" class="text-gray-600">
                  {{ amount }} 
                </li>
              </ul>
            </div>

            <!-- Instructions Section -->
            <div class="mb-6">
              <h3 class="font-semibold mb-3">Instructions</h3>
              <p class="text-sm text-gray-600 whitespace-pre-line">
                {{ recipe.instructions }}
              </p>
            </div>

            <div class="flex justify-between items-center">
              <span class="text-sm text-gray-600">
                {{ recipe.cooking_time_minutes }} mins
              </span>
              <div class="space-x-2">
                <button
                  @click="editRecipe(recipe)"
                  class="px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
                >
                  Edit
                </button>
                <button
                  @click="deleteRecipe(recipe.id)"
                  class="px-3 py-1.5 text-sm bg-red-500 text-white rounded-md hover:bg-red-600"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Create/Edit Modal -->
      <div v-if="showCreateModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
        <div class="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
          <div class="p-6 border-b border-gray-200">
            <h2 class="text-2xl font-bold">{{ editingRecipe ? 'Edit' : 'Create' }} Recipe</h2>
          </div>
          
          <form @submit.prevent="handleSubmit" class="p-6">
            <div class="space-y-6">
              <!-- Group Selection -->
              <div v-if="!editingRecipe">
                <label class="block text-sm font-medium text-gray-700 mb-1">Group</label>
                <select
                  v-model="form.group_id"
                  required
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                >
                  <option value="" disabled>Select group</option>
                  <option v-for="group in groups" :key="group.id" :value="group.id">
                    {{ group.name }}
                  </option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Title</label>
                <input
                  v-model="form.title"
                  required
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  v-model="form.description"
                  rows="3"
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                ></textarea>
              </div>

              <div>
                <Label for="image" class="text-sm font-medium text-gray-700">Recipe Image</Label>
                <div class="mt-1 flex items-center gap-4">
                  <div class="relative">
                    <input
                      type="file"
                      accept="image/*"
                      class="hidden"
                      ref="fileInput"
                      @change="handleImageUpload"
                    />
                    <Button
                      type="button"
                      variant="outline"
                      :disabled="isUploading"
                      @click="() => fileInput?.click()"
                      class="relative"
                    >
                      <div v-if="isUploading" class="absolute inset-0 flex items-center justify-center bg-white/80">
                        <Loader2 class="h-4 w-4 animate-spin" />
                      </div>
                      <div class="flex items-center gap-2">
                        <ImagePlus class="h-4 w-4" />
                        {{ form?.image_url ? 'Change Image' : 'Upload Image' }}
                      </div>
                    </Button>
                  </div>
                  
                  <div v-if="form?.image_url" class="relative h-20 w-20 overflow-hidden rounded-md border">
                    <img
                      :src="form?.image_url"
                      alt="Recipe preview"
                      class="h-full w-full object-cover"
                    />
                    <Button
                      type="button"
                      variant="destructive"
                      size="sm"
                      class="absolute right-1 top-1"
                      @click="form.image_url = ''"
                    >
                      <X class="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                <p class="mt-1 text-sm text-gray-500">
                  Upload a photo of your recipe. PNG, JPG up to 5MB.
                </p>
              </div>

              <div>
                <IngredientParser
                  v-model="form.ingredients"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Instructions</label>
                <textarea
                  v-model="form.instructions"
                  required
                  rows="5"
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                ></textarea>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Cooking Time (minutes)</label>
                <input
                  v-model.number="form.cooking_time_minutes"
                  type="number"
                  required
                  min="1"
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                />
              </div>
            </div>

            <div class="mt-6 flex justify-end space-x-2">
              <button
                type="button"
                @click="closeModal"
                class="px-4 py-2 text-sm border border-gray-300 text-gray-700 bg-white rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                class="px-4 py-2 text-sm bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
              >
                {{ editingRecipe ? 'Update' : 'Create' }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Add Recipe Button -->
      <button
        @click="showCreateModal = true"
        class="fixed bottom-6 right-6 h-12 w-12 rounded-full bg-indigo-600 text-white shadow-lg hover:bg-indigo-700 flex items-center justify-center"
      >
        <Plus class="h-6 w-6" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { recipes as recipesApi, groups as groupsApi } from '@/services/api';
import { useToast } from 'vue-toast-notification';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { ChevronLeft, Plus, ImagePlus, Loader2, X } from 'lucide-vue-next';
import IngredientParser from '@/components/IngredientParser.vue';

const recipes = ref([]);
const groups = ref([]);
const showCreateModal = ref(false);
const editingRecipe = ref(null);
const toast = useToast();

const form = ref({
  title: '',
  description: '',
  instructions: '',
  cooking_time_minutes: 30,
  ingredients: [],
  image_url: '',
  group_id: '',
});

const isUploading = ref(false);
const imageFile = ref(null);
const fileInput = ref(null);

const resetForm = () => {
  form.value = {
    title: '',
    description: '',
    instructions: '',
    cooking_time_minutes: 30,
    ingredients: [],
    image_url: '',
    group_id: '',
  };
  editingRecipe.value = null;
};

const closeModal = () => {
  showCreateModal.value = false;
  resetForm();
};

const fetchRecipes = async () => {
  try {
    const response = await recipesApi.getAll();
    recipes.value = response.data;
  } catch (error) {
    console.error('Failed to fetch recipes:', error);
    toast.error('Failed to fetch recipes');
  }
};

const fetchGroups = async () => {
  try {
    const response = await groupsApi.getAll();
    groups.value = response.data;
    if (groups.value.length > 0) {
      form.value.group_id = groups.value[0].id;
    }
  } catch (error) {
    console.error('Failed to fetch groups:', error);
    toast.error('Failed to fetch groups');
  }
};

const handleSubmit = async () => {
  try {
    if (!form.value.group_id) {
      toast.error('Please select a group');
      return;
    }

    // Format the data for the backend
    const formData = {
      title: form.value.title,
      description: form.value.description || "",
      instructions: form.value.instructions,
      cooking_time_minutes: parseInt(form.value.cooking_time_minutes),
      image_url: form.value.image_url || "",
      group_id: form.value.group_id,
      ingredients: form.value.ingredients
        .filter(ing => ing.name.trim() && ing.amount.trim())
        .map(ing => `${ing.amount} ${ing.name}`.trim())
    };

    if (editingRecipe.value) {
      await recipesApi.update(editingRecipe.value.id, formData);
      toast.success('Recipe updated successfully');
    } else {
      await recipesApi.create(formData);
      toast.success('Recipe created successfully');
    }
    await fetchRecipes();
    showCreateModal.value = false;
    resetForm();
  } catch (error) {
    console.error('Recipe operation failed:', error);
    const errorMessage = error.response?.data?.detail || 'Failed to save recipe';
    toast.error(typeof errorMessage === 'string' ? errorMessage : 'Failed to save recipe');
  }
};

const editRecipe = (recipe) => {
  editingRecipe.value = recipe;
  
  // Parse ingredients strings into objects
  const ingredients = recipe.ingredients.map(ing => {
    const match = ing.match(/^([\d\s./½¼¾⅓⅔]+(?:\s*(?:cup|cups|tablespoon|tablespoons|teaspoon|teaspoons|ounce|ounces|pound|pounds|g|kg|ml|l|oz|lb|tbsp|tsp|c|T|t|g|ml|l)s?)?)?\s*(.+)$/i);
    if (match) {
      const [, amount, name] = match;
      return {
        amount: amount ? amount.trim() : '',
        name: name.trim()
      };
    }
    return { amount: '', name: ing };
  });
  
  form.value = {
    ...recipe,
    ingredients
  };
  showCreateModal.value = true;
};

const deleteRecipe = async (recipeId) => {
  if (confirm('Are you sure you want to delete this recipe?')) {
    try {
      await recipesApi.delete(recipeId);
      toast.success('Recipe deleted successfully');
      await fetchRecipes();
    } catch (error) {
      console.error('Delete failed:', error);
      toast.error(error.response?.data?.detail || 'Failed to delete recipe');
    }
  }
};

const handleImageUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  try {
    isUploading.value = true;
    imageFile.value = file;
    const publicUrl = await storage.uploadRecipeImage(file);
    form.value.image_url = publicUrl;
    toast.success('Image uploaded successfully');
  } catch (error) {
    console.error('Image upload failed:', error);
    toast.error('Failed to upload image');
  } finally {
    isUploading.value = false;
  }
};

onMounted(async () => {
  await fetchGroups();
  await fetchRecipes();
});
</script>
  