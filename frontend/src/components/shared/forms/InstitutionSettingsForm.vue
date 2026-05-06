<template>
  <div class="card border-0 shadow-sm">
    <div class="card-header bg-white border-bottom">
      <h5 class="card-title mb-0 fw-semibold">
        <i class="bi bi-palette me-2 text-admin"></i>
        Public Profile & Branding
      </h5>
    </div>
    <div class="card-body p-4">
      <form @submit.prevent="$emit('submit')">
        <!-- Branding & Design -->
        <div class="mb-5">
          <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
            <i class="bi bi-palette me-2 text-admin"></i>Branding & Design
          </h6>
          <div class="row g-4">
            <div class="col-md-4">
              <label class="form-label d-flex justify-content-between">
                Theme Color
                <span class="badge" :style="{ backgroundColor: modelValue.theme_color || '#3b82f6', color: '#fff' }">
                  {{ modelValue.theme_color || '#3b82f6' }}
                </span>
              </label>
              <input type="color" v-model="modelValue.theme_color" class="form-control form-control-color w-100" style="height: 45px;">
              <div class="form-text mt-2">Main brand color used across the public profile.</div>
            </div>
            <div class="col-md-4">
              <label class="form-label">Institution Logo</label>
              <ImageUpload 
                v-model="modelValue.logo" 
                :existing-image-url="typeof modelValue.logo === 'string' ? modelValue.logo : ''"
                aspect-ratio="1/1"
                placeholder="Upload Logo"
              />
            </div>
            <div class="col-md-4">
              <label class="form-label">Hero Cover Image</label>
              <ImageUpload 
                v-model="modelValue.cover_image" 
                :existing-image-url="typeof modelValue.cover_image === 'string' ? modelValue.cover_image : ''"
                aspect-ratio="16/9"
                placeholder="Upload Hero Banner"
              />
            </div>
            <div class="col-12">
              <BaseInput v-model="modelValue.tagline" label="Tagline / Slogan" type="text" placeholder="e.g., Excellence in Education" />
            </div>
            <div class="col-12">
              <label class="form-label">Footer Custom Text</label>
              <textarea v-model="modelValue.footer_text" class="form-control" rows="2" placeholder="Text to show in the footer..."></textarea>
            </div>
          </div>
        </div>

        <!-- Vision & Mission -->
        <div class="mb-5">
          <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
            <i class="bi bi-eye me-2 text-admin"></i>Vision & Mission
          </h6>
          <div class="row g-4">
            <div class="col-md-6">
              <label class="form-label">Mission Statement</label>
              <textarea v-model="modelValue.mission" class="form-control" rows="4" placeholder="Enter institution mission..."></textarea>
            </div>
            <div class="col-md-6">
              <label class="form-label">Vision Statement</label>
              <textarea v-model="modelValue.vision" class="form-control" rows="4" placeholder="Enter institution vision..."></textarea>
            </div>
          </div>
        </div>

        <!-- Principal Information -->
        <div class="mb-5">
          <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
            <i class="bi bi-person-badge me-2 text-admin"></i>Principal Information
          </h6>
          <div class="row g-4">
            <div class="col-md-8">
              <BaseInput v-model="modelValue.principal_name" label="Principal Name" type="text" placeholder="e.g., Dr. Ahmad Ali" />
              <div class="mt-4">
                <label class="form-label">Principal's Message</label>
                <textarea v-model="modelValue.principal_message" class="form-control" rows="6" placeholder="Enter the message from the principal..."></textarea>
              </div>
            </div>
            <div class="col-md-4">
              <label class="form-label">Principal's Photo</label>
              <ImageUpload 
                v-model="modelValue.principal_image" 
                :existing-image-url="typeof modelValue.principal_image === 'string' ? modelValue.principal_image : ''"
                aspect-ratio="3/4"
                placeholder="Upload Photo"
              />
              <div class="form-text mt-2 text-center">Formal portrait (e.g. 3x4 aspect ratio).</div>
            </div>
          </div>
        </div>

        <!-- Admissions Control -->
        <div class="mb-5">
          <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
            <i class="bi bi-megaphone me-2 text-admin"></i>Admissions & Intake
          </h6>
          <div class="row g-4">
            <div class="col-12">
              <div class="form-check form-switch custom-switch py-2">
                <input class="form-check-input" type="checkbox" id="showAdmissions" v-model="modelValue.show_admissions">
                <label class="form-check-label fw-bold ms-2" for="showAdmissions">
                  Enable Admissions Section
                </label>
                <div class="form-text ms-2">Toggle the visibility of the Admissions tab and all admission-related actions on the public profile.</div>
              </div>
            </div>
            
            <!-- Featured Admission Cards -->
            <div class="col-12 mt-4" :class="{ 'opacity-50 pointer-events-none': !modelValue.show_admissions }">
              <div v-if="!modelValue.show_admissions" class="alert alert-info py-2 px-3 small border-0 shadow-sm rounded-3 mb-3">
                <i class="bi bi-info-circle-fill me-2"></i>
                Admissions section is currently disabled. Enable it above to manage promotional cards.
              </div>

              <div class="d-flex justify-content-between align-items-center mb-3">
                <label class="form-label fw-semibold mb-0">Featured Admission Cards (Promotional)</label>
                <button 
                  type="button" 
                  @click="addFeaturedCard" 
                  class="btn btn-sm btn-admin-outline rounded-pill"
                  :disabled="!modelValue.show_admissions"
                >
                  <i class="bi bi-plus-circle me-1"></i>Add Promotional Card
                </button>
              </div>
              
              <div v-if="!modelValue.featured_admissions || modelValue.featured_admissions.length === 0" class="text-center py-4 border rounded bg-light border-dashed">
                <p class="text-muted mb-0 small">No featured cards added yet. Add cards for programs like FSc, ICS, etc.</p>
              </div>
              
              <div class="row g-3">
                <div v-for="(card, index) in modelValue.featured_admissions" :key="index" class="col-md-6 col-xl-4">
                  <div class="card border shadow-none h-100 featured-card-item">
                    <div class="card-body p-3">
                      <div class="d-flex justify-content-between mb-2">
                        <span class="badge bg-light text-admin border">Card #{{ index + 1 }}</span>
                        <button type="button" @click="removeFeaturedCard(index)" class="btn btn-link text-danger p-0">
                          <i class="bi bi-trash"></i>
                        </button>
                      </div>
                      <BaseInput v-model="card.title" label="Title" placeholder="e.g. FSc Pre-Medical" class="mb-2" />
                      <BaseInput v-model="card.badge_text" label="Badge Text" placeholder="e.g. Admissions Open" class="mb-2" />
                      <textarea v-model="card.description" class="form-control mb-2" rows="2" placeholder="Short description..."></textarea>
                      <label class="form-label small fw-semibold">Card Image</label>
                      <ImageUpload 
                        v-model="card.image" 
                        :existing-image-url="typeof card.image === 'string' ? card.image : ''"
                        aspect-ratio="16/9"
                        placeholder="Card Ad Image"
                        class="mb-2"
                      />
                      <BaseInput v-model="card.link_url" label="Apply Link (Optional)" placeholder="https://..." class="mb-2" />
                      <div class="row g-2">
                        <div class="col-6">
                          <BaseInput v-model="card.admission_start_date" label="Start Date" type="date" />
                        </div>
                        <div class="col-6">
                          <BaseInput v-model="card.admission_end_date" label="End Date" type="date" />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Gallery Customization -->
        <div class="mb-5">
          <h6 class="text-dark fw-semibold mb-3 pb-2 border-bottom">
            <i class="bi bi-images me-2 text-admin"></i>Gallery Customization
          </h6>
          <div class="row g-4">
            <div class="col-12">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <label class="form-label fw-semibold mb-0">Public Profile Gallery Images</label>
              </div>
              <div class="card bg-light border-0 shadow-sm mb-3">
                <div class="card-body">
                  <div class="row align-items-end g-3">
                    <div class="col-md-5">
                      <label class="form-label small fw-semibold">Select Category (Type)</label>
                      <select v-model="newGalleryCategory" class="form-select form-select-sm">
                        <option v-for="opt in categoryOptions" :key="opt" :value="opt">{{ opt.charAt(0).toUpperCase() + opt.slice(1) }}</option>
                      </select>
                    </div>
                    <div class="col-md-5">
                      <label class="form-label small fw-semibold">Upload Bulk Images</label>
                      <input type="file" class="form-control form-control-sm" multiple accept="image/*" @change="handleBulkGalleryUpload" ref="bulkUploadInput">
                    </div>
                  </div>
                  <div class="form-text mt-2">Select a category, then pick up to 10 images at once to add them to your gallery.</div>
                </div>
              </div>
              
              <div v-if="!modelValue.gallery_images || modelValue.gallery_images.length === 0" class="text-center py-4 border rounded bg-light border-dashed">
                <p class="text-muted mb-0 small">No gallery images added yet. Use the upload tool above to add some.</p>
              </div>

              <div class="row g-3">
                <div v-for="(img, index) in modelValue.gallery_images" :key="index" class="col-6 col-md-4 col-xl-3">
                  <div class="card border shadow-sm h-100 position-relative overflow-hidden">
                    <button type="button" @click="removeGalleryImage(index)" class="btn btn-sm btn-danger position-absolute top-0 end-0 m-1 z-3 rounded-circle p-1" style="width: 24px; height: 24px; display: flex; align-items: center; justify-content: center;">
                      <i class="bi bi-x"></i>
                    </button>
                    <div class="ratio ratio-4x3 bg-dark">
                      <img v-if="img.previewUrl || typeof img.image === 'string'" :src="img.previewUrl || img.image" class="object-fit-cover w-100 h-100" />
                      <div v-else class="d-flex align-items-center justify-content-center text-white-50"><i class="bi bi-image"></i></div>
                    </div>
                    <div class="card-body p-2 bg-light">
                      <div class="mb-1">
                        <select v-model="img.category" class="form-select form-select-sm px-1 py-0 text-center fw-bold text-uppercase border-0 bg-transparent text-primary" style="font-size: 0.7rem; box-shadow: none;">
                          <option v-for="opt in categoryOptions" :key="opt" :value="opt">{{ opt }}</option>
                          <option value="other">Other</option>
                        </select>
                      </div>
                      <input type="text" v-model="img.caption" class="form-control form-control-sm px-1 py-0 border-0 bg-transparent text-center" placeholder="Optional caption" style="font-size: 0.8rem;">
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Form Actions -->
        <div class="d-flex gap-3 justify-content-end pt-3 border-top">
          <button type="button" @click="$emit('cancel')" class="btn btn-outline-secondary px-4" :disabled="submitting">
            <i class="bi bi-x-circle me-2"></i>Cancel
          </button>
          <button type="submit" class="btn btn-admin-primary px-4" :disabled="submitting">
            <span v-if="submitting"><span class="spinner-border spinner-border-sm me-2"></span>Saving Settings...</span>
            <span v-else><i class="bi bi-check-circle me-2"></i>Save Profile Settings</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { BaseInput, ImageUpload } from '@/components/shared/common'

const props = defineProps({
  modelValue: { type: Object, required: true },
  submitting: { type: Boolean, default: false }
})

defineEmits(['update:modelValue', 'submit', 'cancel'])

const addFeaturedCard = () => {
  if (!props.modelValue.featured_admissions) {
    props.modelValue.featured_admissions = []
  }
  props.modelValue.featured_admissions.push({
    title: '',
    description: '',
    image: null,
    badge_text: 'Admissions Open',
    link_url: '',
    order: props.modelValue.featured_admissions.length
  })
}

const removeFeaturedCard = (index) => {
  props.modelValue.featured_admissions.splice(index, 1)
}

const categoryOptions = ['campus', 'sports', 'events', 'labs','Gardening','classroom', 'hostel', 'library']
const newGalleryCategory = ref('campus')
const bulkUploadInput = ref(null)

const handleBulkGalleryUpload = (event) => {
  const files = Array.from(event.target.files)
  if (!files.length) return
  
  if (!props.modelValue.gallery_images) {
    props.modelValue.gallery_images = []
  }

  files.forEach(file => {
    const previewUrl = URL.createObjectURL(file)
    props.modelValue.gallery_images.push({
      image: file,
      previewUrl: previewUrl,
      category: newGalleryCategory.value || 'campus',
      caption: file.name.split('.')[0]
    })
  })

  // Clear input so same files can be re-selected if needed
  if (bulkUploadInput.value) {
    bulkUploadInput.value.value = ''
  }
}

const removeGalleryImage = (index) => {
  const img = props.modelValue.gallery_images[index]
  if (img.previewUrl) {
    URL.revokeObjectURL(img.previewUrl)
  }
  props.modelValue.gallery_images.splice(index, 1)
}
</script>

<style scoped>
.cursor-pointer {
  cursor: pointer;
}
.transition-all {
  transition: all 0.2s ease-in-out;
}
</style>
