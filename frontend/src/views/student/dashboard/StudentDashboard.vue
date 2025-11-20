<template>
  <!-- Welcome Section -->
  <div class="mb-5">
    <h1 class="h2 fw-bold text-dark mb-2">Student Dashboard</h1>
    <p class="text-muted">Welcome back! Continue your learning journey.</p>
  </div>

  <!-- Stats Grid -->
  <div class="row g-4 mb-5">
    <div class="col-12 col-md-6 col-lg-3">
      <StatCard
        title="Enrolled Courses"
        value="6"
        change="+1%"
        icon="bi bi-book-open"
        bg-color="bg-info bg-opacity-10"
        icon-color="text-info"
        :is-positive="true"
      />
    </div>
    <div class="col-12 col-md-6 col-lg-3">
      <StatCard
        title="Pending Assignments"
        value="4"
        change="+2%"
        icon="bi bi-clipboard-check"
        bg-color="bg-warning bg-opacity-10"
        icon-color="text-warning"
        :is-positive="false"
      />
    </div>
    <div class="col-12 col-md-6 col-lg-3">
      <StatCard
        title="Current GPA"
        value="3.8"
        change="+0.2%"
        icon="bi bi-bar-chart"
        bg-color="bg-success bg-opacity-10"
        icon-color="text-success"
        :is-positive="true"
      />
    </div>
    <div class="col-12 col-md-6 col-lg-3">
      <StatCard
        title="Attendance"
        value="95%"
        change="+2%"
        icon="bi bi-calendar"
        bg-color="bg-primary bg-opacity-10"
        icon-color="text-primary"
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
            title="View Assignments"
            description="Check pending work"
            icon="bi bi-clipboard-check"
            bg-gradient="bg-info bg-opacity-10"
            icon-bg-color="bg-info bg-opacity-20"
            icon-color="text-info"
          />
        </div>
        <div class="col-12 col-md-6">
          <QuickActionCard
            title="View Grades"
            description="Check your scores"
            icon="bi bi-bar-chart"
            bg-gradient="bg-success bg-opacity-10"
            icon-bg-color="bg-success bg-opacity-20"
            icon-color="text-success"
          />
        </div>
        <div class="col-12 col-md-6">
          <QuickActionCard
            title="Class Schedule"
            description="View timetable"
            icon="bi bi-calendar"
            bg-gradient="bg-primary bg-opacity-10"
            icon-bg-color="bg-primary bg-opacity-20"
            icon-color="text-primary"
          />
        </div>
        <div class="col-12 col-md-6">
          <QuickActionCard
            title="Download Materials"
            description="Course resources"
            icon="bi bi-download"
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
import { recentActivities } from '@/pannel/student.js'
</script>
