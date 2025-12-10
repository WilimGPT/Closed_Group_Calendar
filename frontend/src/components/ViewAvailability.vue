<template>
  <div class="form-card wide">

    <h2>View Availability & Courses</h2>

    <!-- Language -->
    <div class="form-row">
      <label>Language</label>
      <el-select v-model="language">
        <el-option label="English" value="english" />
        <el-option label="Spanish" value="spanish" />
        <el-option label="German" value="german" />
      </el-select>
    </div>

    <!-- Teacher -->
    <div class="form-row" v-if="teachers.length">
      <label>Teacher</label>
      <el-select v-model="teacherId">
        <el-option
          v-for="t in teachers"
          :key="t.id"
          :label="t.name"
          :value="t.id"
        />
      </el-select>
    </div>

    <el-divider />

    <!-- TWO COLUMN LAYOUT -->
    <div class="two-col" v-if="teacherId">

      <!-- LEFT: AVAILABILITY -->
      <div>
        <h3 class="mb-3">Active Availability Slots</h3>

        <div v-if="activeSlots.length">
          <div
            v-for="slot in activeSlots"
            :key="slot.id"
            class="slot-card"
          >
            <div><strong>Weekday:</strong> {{ weekdays[slot.weekday] }}</div>
            <div><strong>Time:</strong> {{ slot.startTime }} – {{ slot.endTime }}</div>
            <div><strong>Valid:</strong> {{ slot.startDate }} → {{ slot.endDate }}</div>
            <div><strong>Time Zone:</strong> {{ slot.timeZone }}</div>
            <div><strong>Slot ID:</strong> {{ slot.id }}</div>
          </div>
        </div>

        <div v-else class="text-muted mb-4">
          No currently active availability slots.
        </div>

        <el-divider />

        <h3 class="mb-3">Future Availability Slots</h3>

        <div v-if="futureSlots.length">
          <div
            v-for="slot in futureSlots"
            :key="slot.id"
            class="slot-card future"
          >
            <div><strong>Weekday:</strong> {{ weekdays[slot.weekday] }}</div>
            <div><strong>Time:</strong> {{ slot.startTime }} – {{ slot.endTime }}</div>
            <div><strong>Valid:</strong> {{ slot.startDate }} → {{ slot.endDate }}</div>
            <div><strong>Time Zone:</strong> {{ slot.timeZone }}</div>
            <div><strong>Slot ID:</strong> {{ slot.id }}</div>
          </div>
        </div>

        <div v-else class="text-muted">
          No future availability slots.
        </div>
      </div>

      <!-- RIGHT: COURSES -->
      <div>
        <h3 class="mb-3">Current Courses</h3>

        <div v-if="currentCourses.length">
          <div
            v-for="course in currentCourses"
            :key="course.id"
            class="course-card"
          >
            <div><strong>Group:</strong> {{ course.groupReference }}</div>
            <div><strong>Sessions:</strong></div>
            <ul>
              <li v-for="s in course.sessions" :key="s.id">
                {{ s.startDateTime }}
              </li>
            </ul>
          </div>
        </div>

        <div v-else class="text-muted mb-4">
          No current courses.
        </div>

        <el-divider />

        <h3 class="mb-3">Future Courses</h3>

        <div v-if="futureCourses.length">
          <div
            v-for="course in futureCourses"
            :key="course.id"
            class="course-card future"
          >
            <div><strong>Group:</strong> {{ course.groupReference }}</div>
            <div><strong>Sessions:</strong></div>
            <ul>
              <li v-for="s in course.sessions" :key="s.id">
                {{ s.startDateTime }}
              </li>
            </ul>
          </div>
        </div>

        <div v-else class="text-muted">
          No future courses.
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import api from "../api"

export default {
  data() {
    return {
      language: "english",
      teachers: [],
      teacherId: "",

      activeSlots: [],
      futureSlots: [],

      currentCourses: [],
      futureCourses: [],

      weekdays: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    }
  },

  watch: {
    language() {
      this.loadTeachers()
    },
    teacherId() {
      this.filterAll()
    }
  },

  mounted() {
    this.loadTeachers()
  },

  methods: {
    async loadTeachers() {
      const res = await api.get(this.language)
      this.teachers = res.data.teachers
      this.teacherId = ""

      this.activeSlots = []
      this.futureSlots = []
      this.currentCourses = []
      this.futureCourses = []
    },

    filterAll() {
      const teacher = this.teachers.find(t => t.id === this.teacherId)
      if (!teacher) return

      const today = new Date().toISOString().slice(0, 10)

      // ---- AVAILABILITY ----

      const validSlots = teacher.availabilitySlots.filter(
        s => s.endDate >= today
      )

      this.activeSlots = validSlots.filter(
        s => s.startDate <= today && s.endDate >= today
      )

      this.futureSlots = validSlots.filter(
        s => s.startDate > today
      )

      // ---- COURSES ----

        const allCourses = teacher.bookings || []

        this.currentCourses = allCourses.filter(course => {
        const dates = course.sessions.map(s => s.startDateTime.slice(0, 10))
        const firstDate = dates.reduce((a, b) => (a < b ? a : b))
        const lastDate = dates.reduce((a, b) => (a > b ? a : b))

        // current = already started, not finished
        return firstDate <= today && lastDate >= today
        })

        this.futureCourses = allCourses.filter(course => {
        const dates = course.sessions.map(s => s.startDateTime.slice(0, 10))
        const firstDate = dates.reduce((a, b) => (a < b ? a : b))

        // future = not started yet
        return firstDate > today
        })
    }
  }
}
</script>

<style scoped>
.form-card.wide {
  max-width: 1100px;
}

.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
}

.slot-card,
.course-card {
  background: #f5f8ff;
  border: 1px solid #dbe4ff;
  border-radius: 6px;
  padding: 12px 14px;
  margin-bottom: 10px;
  font-size: 13px;
}

.slot-card.future,
.course-card.future {
  background: #f7fff5;
  border-color: #cfe9d6;
}

.course-card ul {
  padding-left: 18px;
  margin: 6px 0 0;
}

.text-muted {
  color: #888;
}
</style>
