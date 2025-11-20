<template>
  <!-- Welcome Section -->
  <div class="mb-5">
    <h1 class="h2 fw-bold text-dark mb-2">Admin Dashboard</h1>
    <p class="text-muted">Welcome back! Here's what's happening at your college today.</p>
  </div>

  <!-- Stats Grid -->
  <div class="row g-4 mb-5">
    <div class="col-xl-3 col-md-6">
      <StatCard
        title="Total Students"
        value="2,847"
        change="+12%"
        icon="bi bi-people"
        bg-color="bg-primary-light"
        icon-color="text-primary"
        :is-positive="true"
      />
    </div>
    <div class="col-xl-3 col-md-6">
      <StatCard
        title="Total Teachers"
        value="156"
        change="+3%"
        icon="bi bi-person-badge"
        bg-color="bg-success-light"
        icon-color="text-success"
        :is-positive="true"
      />
    </div>
    <div class="col-xl-3 col-md-6">
      <StatCard
        title="Total Departments"
        value="24"
        change="+1%"
        icon="bi bi-building"
        bg-color="bg-info-light"
        icon-color="text-info"
        :is-positive="true"
      />
    </div>
    <div class="col-xl-3 col-md-6">
      <StatCard
        title="Total Revenue"
        value="$45,678"
        change="+8%"
        icon="bi bi-currency-dollar"
        bg-color="bg-warning-light"
        icon-color="text-warning"
        :is-positive="true"
      />
    </div>
  </div>

  <!-- Content Grid -->
  <div class="row g-4">
    <!-- Recent Activities -->
    <div class="col-lg-6">
      <ActivityFeed :activities="recentActivities" />
    </div>

    <!-- Quick Actions -->
    <div class="col-lg-6">
      <div class="card border-0 shadow-sm h-100">
        <div class="card-body">
          <h5 class="card-title fw-semibold text-dark mb-4">Quick Actions</h5>
          <div class="row g-3">
            <div class="col-md-6">
              <QuickActionCard
                title="Add Student"
                description="Enroll new student"
                icon="bi bi-person-plus"
                bg-gradient="bg-light"
                icon-bg-color="bg-primary-light"
                icon-color="text-primary"
              />
            </div>
            <div class="col-md-6">
              <QuickActionCard
                title="Add Teacher"
                description="Register new teacher"
                icon="bi bi-person-badge"
                bg-gradient="bg-light"
                icon-bg-color="bg-success-light"
                icon-color="text-success"
              />
            </div>
            <div class="col-md-6">
              <QuickActionCard
                title="Add Department"
                description="Create new department"
                icon="bi bi-building"
                bg-gradient="bg-light"
                icon-bg-color="bg-info-light"
                icon-color="text-info"
              />
            </div>
            <div class="col-md-6">
              <QuickActionCard
                title="Collect Fees"
                description="Process payments"
                icon="bi bi-currency-dollar"
                bg-gradient="bg-light"
                icon-bg-color="bg-warning-light"
                icon-color="text-warning"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import StatCard from '@/components/common/StatCard.vue'
import ActivityFeed from '@/components/common/ActivityFeed.vue'
import QuickActionCard from '@/components/common/QuickActionCard.vue'
import { recentActivities } from '@/pannel/admin.js'
</script>