<template>
	<div class="container-fluid py-3 px-2 px-md-3 productivity-page">
		<div class="row justify-content-center mb-4">
			<div class="col-12 col-md-9 col-lg-7">
				<div class="card border-0 rounded-4 shadow-sm taskflow-header">
					<div class="card-body py-3 px-4 text-center">
						<h2 class="h3 fw-bold text-white mb-2 d-flex align-items-center justify-content-center gap-2">
							<i class="bi bi-clipboard2-check-fill text-student-accent"></i>
							TaskFlow
						</h2>
						<p class="mb-0 fw-medium small text-student-accent">Organize your day &bull; beautiful cards &bull; smart due dates</p>
					</div>
				</div>
			</div>
		</div>

		<div class="card border-0 rounded-4 shadow-sm mb-3 main-card">
			<div class="card-body p-3 p-md-4 student-soft-bg">
				<h6 class="text-uppercase fw-bold text-secondary small mb-3">Add Task</h6>
				<form @submit.prevent="addTask" class="row g-3 align-items-end">
					<div class="col-lg-6">
						<label class="form-label text-uppercase fw-bold text-secondary small mb-2">
							<i class="bi bi-pencil-fill me-1"></i> Task Name
						</label>
						<input
							v-model.trim="draft.title"
							type="text"
							class="form-control rounded-pill task-input"
							placeholder="e.g., Design dashboard, call with team"
							required
						>
					</div>

					<div class="col-lg-3">
						<label class="form-label text-uppercase fw-bold text-secondary small mb-2">
							<i class="bi bi-calendar-event-fill me-1"></i> Due Date
						</label>
						<div class="date-input-wrap">
							<BaseInput
								v-model="draft.dueDate"
								type="date"
								placeholder="Select due date"
							/>
						</div>
					</div>

					<div class="col-lg-3">
						<button type="submit" class="btn btn-student-primary w-100 rounded-pill fw-bold" :disabled="!draft.title">
							<i class="bi bi-plus-circle-fill me-2"></i>Add
						</button>
					</div>
				</form>
			</div>
		</div>

		<div class="card border-0 rounded-4 shadow-sm mb-3 main-card">
			<div class="card-body p-3 p-md-4 student-soft-bg">
				<h6 class="text-uppercase fw-bold text-secondary small mb-3">Filters And Overview</h6>
				<div class="row g-3 align-items-center">
					<div class="col-lg-6">
						<div class="card border-0 rounded-pill student-pill-bg main-card">
							<div class="card-body p-2">
								<div class="btn-group w-100" role="group" aria-label="Task filters">
									<button
										v-for="filter in FILTERS"
										:key="filter"
										type="button"
										class="btn rounded-pill fw-semibold small"
										:class="activeFilter === filter ? 'btn-student-primary text-white' : 'text-secondary'"
										@click="activeFilter = filter"
									>
										{{ filter }}
									</button>
								</div>
							</div>
						</div>
					</div>

					<div class="col-lg-6 d-flex justify-content-lg-end">
						<div class="card border-0 rounded-pill student-stat-bg shadow-sm main-card">
							<div class="card-body py-2 px-3 fw-semibold text-dark d-flex align-items-center gap-2">
								<span class="text-secondary"><i class="bi bi-card-list me-1"></i>{{ stats.total }} Total</span>
								<span class="text-muted">•</span>
								<span class="text-success">{{ stats.active }} Active</span>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>

		<div class="card border-0 rounded-4 shadow-sm main-card">
			<div class="card-body p-3 p-md-4 student-soft-bg">
				<div class="mb-3">
					<button
						v-if="stats.completed > 0"
						type="button"
						class="btn btn-student-outline rounded-pill px-3 py-1"
						@click="clearCompleted"
					>
						<i class="bi bi-trash-fill me-2"></i>Clear completed
					</button>
				</div>

				<div v-if="filteredTasks.length" class="d-grid gap-3">
					<div
						v-for="task in filteredTasks"
						:key="task.id"
						class="card border-0 rounded-4 shadow-sm task-item main-card"
					>
						<div class="card-body p-3 d-flex justify-content-between align-items-center gap-3">
							<div class="d-flex align-items-start gap-3 flex-grow-1 min-w-0">
								<div class="form-check mt-1">
									<input
										:id="`task-${task.id}`"
										v-model="task.completed"
										class="form-check-input task-check"
										type="checkbox"
									>
								</div>
								<div class="min-w-0 flex-grow-1" @dblclick="startEdit(task)">
									<div v-if="editingId === task.id && !task.completed">
										<input
											v-model="editTitle"
											@blur="saveEdit(task)"
											@keyup.enter="saveEdit(task)"
											@keyup.esc="cancelEdit"
											class="form-control form-control-sm rounded-pill task-input mb-1"
											type="text"
											autofocus
										>
									</div>
									<template v-else>
										<h5 class="mb-1 fw-bold text-truncate fs-6" :class="task.completed ? 'text-decoration-line-through text-secondary' : 'text-dark'">
											{{ task.title }}
										</h5>
										<span v-if="task.dueDate" class="badge student-badge fw-semibold rounded-pill px-2 py-1">
											<i class="bi bi-calendar-check me-1 text-student"></i>{{ formatDate(task.dueDate) }}
										</span>
									</template>
								</div>
							</div>

							<div class="d-flex align-items-center gap-2">
								<button
									v-if="!task.completed"
									type="button"
									class="btn btn-link text-secondary p-0 task-action-btn"
									title="Edit task"
									@click="startEdit(task)"
								>
									<i class="bi bi-pencil-fill fs-5"></i>
								</button>
								<button
									type="button"
									class="btn btn-link text-secondary p-0 task-action-btn"
									title="Delete task"
									@click="deleteTask(task.id)"
								>
									<i class="bi bi-trash3-fill fs-5"></i>
								</button>
							</div>
						</div>
					</div>
				</div>

				<div v-else class="card border-0 rounded-4 student-empty shadow-sm main-card">
					<div class="card-body text-center py-4 text-secondary fw-semibold">
						No tasks yet. Add your first task.
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { BaseInput } from '@/components/shared/common'

const STORAGE_KEY = 'student_productivity_tasks_v2'
const FILTERS = ['All', 'Active', 'Completed']

const tasks = ref([])
const draft = ref({ title: '', dueDate: '' })
const activeFilter = ref('All')

const editingId = ref(null)
const editTitle = ref('')

onMounted(() => {
	const saved = localStorage.getItem(STORAGE_KEY)
	if (!saved) return
	try {
		const parsed = JSON.parse(saved)
		tasks.value = Array.isArray(parsed) ? parsed : []
	} catch {
		tasks.value = []
	}
})

watch(tasks, (value) => {
	localStorage.setItem(STORAGE_KEY, JSON.stringify(value))
}, { deep: true })

const filteredTasks = computed(() => {
	if (activeFilter.value === 'Active') return tasks.value.filter((task) => !task.completed)
	if (activeFilter.value === 'Completed') return tasks.value.filter((task) => task.completed)
	return tasks.value
})

const stats = computed(() => {
	const total = tasks.value.length
	const completed = tasks.value.filter((task) => task.completed).length
	return {
		total,
		completed,
		active: total - completed
	}
})

const addTask = () => {
	if (!draft.value.title) return

	tasks.value.unshift({
		id: Date.now(),
		title: draft.value.title,
		dueDate: draft.value.dueDate,
		completed: false
	})

	draft.value = { title: '', dueDate: '' }
}

const deleteTask = (id) => {
	tasks.value = tasks.value.filter((task) => task.id !== id)
}

const startEdit = (task) => {
	if (task.completed) return
	editingId.value = task.id
	editTitle.value = task.title
}

const saveEdit = (task) => {
	if (editingId.value !== task.id) return
	const val = editTitle.value.trim()
	if (val) {
		task.title = val
	}
	editingId.value = null
}

const cancelEdit = () => {
	editingId.value = null
}

const clearCompleted = () => {
	tasks.value = tasks.value.filter((task) => !task.completed)
}

const formatDate = (dateString) => {
	if (!dateString) return ''
	return new Date(dateString).toLocaleDateString('en-US', {
		month: '2-digit',
		day: '2-digit',
		year: 'numeric'
	})
}
</script>

<style scoped> </style>