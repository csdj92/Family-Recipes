<template>
  <div class="space-y-6">
    <!-- Bulk Input -->
    <div>
      <Label class="text-sm font-medium text-gray-700">Quick Add Ingredients</Label>
      <Textarea
        v-model="bulkText"
        placeholder="Paste your ingredient list here (e.g. '1 cup butter, 2 cups flour')"
        class="mt-1 w-full"
        rows="4"
      />
      <div class="mt-2 flex justify-end">
        <Button 
          type="button"
          variant="secondary"
          size="sm"
          @click="parseAndAdd"
        >
          Parse Ingredients
        </Button>
      </div>
    </div>

    <!-- Individual Ingredients -->
    <div>
      <div class="flex justify-between items-center mb-2">
        <Label class="text-sm font-medium text-gray-700">Ingredients</Label>
        <Button
          type="button"
          variant="outline"
          size="sm"
          @click="addIngredient"
          class="inline-flex items-center"
        >
          <Plus class="mr-2 h-4 w-4" />
          Add Ingredient
        </Button>
      </div>
      
      <div class="space-y-2">
        <div v-for="(ingredient, index) in modelValue" :key="index" class="flex gap-2">
          <Input
            v-model="ingredient.amount"
            placeholder="Amount (e.g., 1 cup)"
            class="w-1/3"
          />
          <Input
            v-model="ingredient.name"
            placeholder="Ingredient name"
            class="flex-1"
          />
          <Button
            type="button"
            variant="destructive"
            size="sm"
            @click="removeIngredient(index)"
          >
            <Trash2 class="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Plus, Trash2 } from 'lucide-vue-next';

const props = defineProps({
  modelValue: {
    type: Array,
    required: true
  }
});

const emit = defineEmits(['update:modelValue']);

const bulkText = ref('');

const parseIngredient = (text) => {
  const match = text.trim().match(/^([\d\s./½¼¾⅓⅔]+(?:\s*(?:cup|cups|tablespoon|tablespoons|teaspoon|teaspoons|ounce|ounces|pound|pounds|g|kg|ml|l|oz|lb|tbsp|tsp|c|T|t|g|ml|l)s?)?)?\s*(.+)$/i);
  
  if (match) {
    const [, amount, name] = match;
    return {
      amount: amount ? amount.trim() : '',
      name: name.trim()
    };
  }
  return null;
};

const parseAndAdd = () => {
  const lines = bulkText.value
    .split(/[,\n]/)
    .filter(line => line.trim());

  const newIngredients = lines
    .map(parseIngredient)
    .filter(ing => ing && ing.name);

  emit('update:modelValue', [...props.modelValue, ...newIngredients]);
  bulkText.value = '';
};

const addIngredient = () => {
  emit('update:modelValue', [...props.modelValue, { amount: '', name: '' }]);
};

const removeIngredient = (index) => {
  const newIngredients = [...props.modelValue];
  newIngredients.splice(index, 1);
  emit('update:modelValue', newIngredients);
};
</script> 