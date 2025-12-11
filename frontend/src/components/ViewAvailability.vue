<template>
  <div class="form-card wide">
    <h2>View Availability & Courses</h2>

    <!-- LANGUAGE SELECTOR -->
    <div class="form-row">
      <label>Language</label>
      <el-select v-model="language">
        <el-option label="English" value="english" />
        <el-option label="Spanish" value="spanish" />
        <el-option label="German" value="german" />
      </el-select>
    </div>

    <!-- TEACHER SELECTOR -->
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

      <!-- LEFT: AVAILABILITY SECTION -->
      <div>
        <h3 class="mb-3">Active Availability Slots</h3>

        <div v-if="activeSlots.length">
          <div
            class="slot-card"
            v-for="slot in activeSlots"
            :key="slot.id"
          >
            <div><strong>Weekdays:</strong> {{ formatWeekdays(slot.weekdays) }}</div>
            <div><strong>Time:</strong> {{ slot.startTime }} – {{ slot.endTime }}</div>
            <div><strong>Valid:</strong> {{ slot.startDate }} → {{ slot.endDate }}</div>
            <div><strong>Time Zone:</strong> {{ slot.timeZone }}</div>
            <div><strong>Slot ID:</strong> {{ slot.id }}</div>
          </div>
        </div>

        <div v-else class="text-muted mb-4">No currently active availability slots.</div>

        <el-divider />

        <!-- FUTURE SLOTS (CLICKABLE FOR EDITING) -->
        <h3 class="mb-3">Future Availability Slots</h3>

        <div v-if="futureSlots.length">
          <div
            class="slot-card future clickable"
            v-for="slot in futureSlots"
            :key="slot.id"
            @click="openEdit(slot)"
          >
            <div><strong>Weekdays:</strong> {{ formatWeekdays(slot.weekdays) }}</div>
            <div><strong>Time:</strong> {{ slot.startTime }} – {{ slot.endTime }}</div>
            <div><strong>Valid:</strong> {{ slot.startDate }} → {{ slot.endDate }}</div>
            <div><strong>Time Zone:</strong> {{ slot.timeZone }}</div>
            <div><strong>Slot ID:</strong> {{ slot.id }}</div>
            <small class="text-muted">(Click to edit)</small>
          </div>
        </div>

        <div v-else class="text-muted">No future availability slots.</div>
      </div>

      <!-- RIGHT: COURSES SECTION -->
      <div>
        <h3 class="mb-3">Current Courses</h3>

        <div v-if="currentCourses.length">
          <div
            class="course-card"
            v-for="course in currentCourses"
            :key="course.id"
          >
            <div><strong>Group:</strong> {{ course.groupReference }}</div>
            <div><strong>Sessions:</strong></div>
            <ul>
              <li v-for="s in course.sessions" :key="s.id">{{ s.startDateTime }}</li>
            </ul>
          </div>
        </div>
        <div v-else class="text-muted mb-4">No current courses.</div>

        <el-divider />

        <h3 class="mb-3">Future Courses</h3>

        <div v-if="futureCourses.length">
          <div
            class="course-card future"
            v-for="course in futureCourses"
            :key="course.id"
          >
            <div><strong>Group:</strong> {{ course.groupReference }}</div>
            <div><strong>Sessions:</strong></div>
            <ul>
              <li v-for="s in course.sessions" :key="s.id">{{ s.startDateTime }}</li>
            </ul>
          </div>
        </div>
        <div v-else class="text-muted">No future courses.</div>
      </div>
    </div>

    <!-- ================================
         EDIT AVAILABILITY MODAL
    ================================= -->
    <el-dialog
      title="Edit Availability Slot"
      :visible.sync="showEditModal"
      width="480px"
    >
      <AvailabilityForm
        :initialSlot="selectedSlot"
        :teacherId="teacherId"
        :language="language"
        :mode="'edit'"
        @saved="handleSaved"
        @deleted="handleDeleted"
        @close="showEditModal = false"
      />
    </el-dialog>

  </div>
</template>

<script>
import api from "../api"
import AvailabilityForm from "./AvailabilityForm.vue"

export default {
  components: { AvailabilityForm },

  data() {
    return {
      language: "english",
      teachers: [],
      teacherId: "",

      activeSlots: [],
      futureSlots: [],

      currentCourses: [],
      futureCourses: [],

      showEditModal: false,
      selectedSlot: null,

      weekdayNames: {
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
        7: "Sunday"
      }
    }
  },

  watch: {
    language() { this.loadTeachers() },
    teacherId() { this.filterAll() }
  },

  mounted() {
    this.loadTeachers()
  },

  methods: {
    /** Reload teachers & reset everything when language changes */
    async loadTeachers() {
      const res = await api.get(this.language)
      this.teachers = res.data.teachers
      this.teacherId = ""
      this.activeSlots = []
      this.futureSlots = []
      this.currentCourses = []
      this.futureCourses = []
    },

    /** Convert [1,2,3] → "Mon, Tue, Wed" */
    formatWeekdays(arr) {
      if (!Array.isArray(arr)) return "–"
      return arr.map(w => this.weekdayNames[w]).join(", ")
    },

    /** Recomputes availability + course lists */
    filterAll() {
      const teacher = this.teachers.find(t => t.id === this.teacherId)
      if (!teacher) return

      const today = new Date().toISOString().slice(0, 10)

      const validSlots = teacher.availabilitySlots.filter(s => s.endDate >= today)

      this.activeSlots = validSlots.filter(s => s.startDate <= today)
      this.futureSlots = validSlots.filter(s => s.startDate > today)

      const allCourses = teacher.bookings || []

      this.currentCourses = allCourses.filter(course => {
        const dates = course.sessions.map(s => s.startDateTime.slice(0, 10))
        const first = Math.min(...dates)
        const last = Math.max(...dates)
        return first <= today && last >= today
      })

      this.futureCourses = allCourses.filter(course => {
        const first = Math.min(...course.sessions.map(s => s.startDateTime.slice(0, 10)))
        return first > today
      })
    },

    /** Opens modal and loads clicked slot */
    openEdit(slot) {
      this.selectedSlot = { ...slot } // shallow copy for safety
      this.showEditModal = true
    },

    /** Called when form saves slot */
    handleSaved() {
      this.showEditModal = false
      this.loadTeachers().then(() => this.filterAll())
    },

    /** Called when slot is deleted */
    handleDeleted() {
      this.showEditModal = false
      this.loadTeachers().then(() => this.filterAll())
    }
  }
}
</script>

<style scoped>
.form-card.wide { max-width: 1100px; }

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

.slot-card.future { background: #f7fff5; border-color: #cfe9d6; }
.course-card.future { background: #f7fff5; border-color: #cfe9d6; }

.clickable { cursor: pointer; }
.clickable:hover { background: #eaf7ff; }

.text-muted { color: #888; }
</style>
