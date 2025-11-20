<template>
  <!-- Welcome Section -->
  <div class="mb-5">
    <h1 class="h2 fw-bold text-dark mb-2">Teacher Dashboard</h1>
    <p class="text-muted">Welcome back! Manage your classes and students.</p>
  </div>

  <!-- Stats Grid -->
  <div class="row g-4 mb-5">
    <div class="col-12 col-md-6 col-lg-3">
      <StatCard
        title="Total Classes"
        value="4"
        change="+1%"
        icon="bi bi-mortarboard"
        bg-color="bg-primary bg-opacity-10"
        icon-color="text-primary"
        :is-positive="true"
      />
    </div>
    <div class="col-12 col-md-6 col-lg-3">
      <StatCard
        title="Total Students"
        value="128"
        change="+5%"
        icon="bi bi-people"
        bg-color="bg-success bg-opacity-10"
        icon-color="text-success"
        :is-positive="true"
      />
    </div>
    <div class="col-12 col-md-6 col-lg-3">
      <StatCard
        title="Pending Assignments"
        value="12"
        change="+3%"
        icon="bi bi-clipboard-check"
        bg-color="bg-warning bg-opacity-10"
        icon-color="text-warning"
        :is-positive="false"
      />
    </div>
    <div class="col-12 col-md-6 col-lg-3">
      <StatCard
        title="Avg. Class Score"
        value="82%"
        change="+4%"
        icon="bi bi-bar-chart"
        bg-color="bg-info bg-opacity-10"
        icon-color="text-info"
        :is-positive="true"
      />
    </div>
  </div>

  <div class="row g-4">
    <!-- Recent Activities -->
    <div class="col-12 col-lg-6">
      <ActivityFeed :activities="recentActivities" />
    </div>

    <!-- Quick Actions -->
    <div class="col-12 col-lg-6">
      <h3 class="h5 fw-semibold text-dark mb-4">Quick Actions</h3>
      <div class="row g-3">
        <div class="col-12 col-md-6">
          <QuickActionCard
            title="Create Assignment"
            description="Add new assignment"
            icon="bi bi-file-plus"
            bg-gradient="bg-primary bg-opacity-10"
            icon-bg-color="bg-primary bg-opacity-20"
            icon-color="text-primary"
          />
        </div>
        <div class="col-12 col-md-6">
          <QuickActionCard
            title="Grade Submissions"
            description="Review student work"
            icon="bi bi-check-circle"
            bg-gradient="bg-success bg-opacity-10"
            icon-bg-color="bg-success bg-opacity-20"
            icon-color="text-success"
          />
        </div>
        <div class="col-12 col-md-6">
          <QuickActionCard
            title="Post Grades"
            description="Publish scores"
            icon="bi bi-bar-chart"
            bg-gradient="bg-info bg-opacity-10"
            icon-bg-color="bg-info bg-opacity-20"
            icon-color="text-info"
          />
        </div>
        <div class="col-12 col-md-6">
          <QuickActionCard
            title="Class Attendance"
            description="Mark attendance"
            icon="bi bi-calendar"
            bg-gradient="bg-warning bg-opacity-10"
            icon-bg-color="bg-warning bg-opacity-20"
            icon-color="text-warning"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import StatCard from '@/components/common/StatCard.vue'
import ActivityFeed from '@/components/common/ActivityFeed.vue'
import QuickActionCard from '@/components/common/QuickActionCard.vue'
import { recentActivities } from '@/pannel/teacher.js'
</script>
