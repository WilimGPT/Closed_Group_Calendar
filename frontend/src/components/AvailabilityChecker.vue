
<template>
  <div class="form-card wide">
    <h2>Availability Checker</h2>

    <!-- INPUT PANEL -->
    <div class="checker-grid">

      <div class="form-row">
        <label>Language</label>
        <el-select v-model="language">
          <el-option label="English" value="english" />
          <el-option label="Spanish" value="spanish" />
          <el-option label="German" value="german" />
        </el-select>
      </div>

      <div class="form-row">
        <label>Day of Week</label>
        <el-select v-model="weekday">
          <el-option v-for="(d, i) in weekdays" :key="i" :label="d" :value="i" />
        </el-select>
      </div>

      <div class="form-row">
        <label>Start Time</label>
        <el-time-picker v-model="startTime" format="HH:mm" />
      </div>

      <div class="form-row">
        <label>Start Date</label>
        <el-date-picker v-model="startDate" type="date" />
      </div>

      <div class="form-row">
        <label>Number of Sessions</label>
        <el-input-number v-model="sessionCount" :min="1" />
      </div>

      <div class="form-row">
        <label>Duration (minutes)</label>
        <el-input-number v-model="duration" :step="15" />
      </div>

      <div class="form-row">
        <label>Time Zone</label>
        <el-select v-model="timeZone" filterable>
          <el-option
            v-for="tz in timezones"
            :key="tz"
            :label="tz"
            :value="tz"
          />
        </el-select>
      </div>

    </div>

    <el-button type="primary" class="mt-4" @click="runCheck">
      Confirm & Check
    </el-button>

    <!-- RESULT TABLE -->
    <div v-if="results.length" class="mt-6 table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Session (Local / UTC)</th>
            <th v-for="t in teachers" :key="t.id">
              {{ t.name }}
            </th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="(row, i) in results" :key="i">
            <td>
              {{ row.local }}  
              <br />
              <small class="text-muted">{{ row.utc }}</small>
            </td>

            <td
              v-for="cell in row.statuses"
              :key="cell.teacherId"
              :class="cell.ok ? 'status-ok' : 'status-bad'"
            >
              {{ cell.message }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>

<script>
import api from "../api"
import timezones from "../timezones"

export default {
  data() {
    return {
      language: "english",
      weekday: 1,
      startTime: "",
      startDate: "",
      sessionCount: 5,
      duration: 60,
      timeZone: "Europe/Warsaw",

      teachers: [],
      results: [],

      timezones,

      weekdays: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    }
  },

  methods: {
    async runCheck() {
      const res = await api.get(this.language)
      this.teachers = res.data.teachers

      const sessions = this.generateSessions()
      this.results = sessions.map(session => {
        const statuses = this.teachers.map(teacher =>
          this.checkTeacher(teacher, session)
        )

        return {
          local: session.localLabel,
          utc: session.utcLabel,
          statuses
        }
      })
    },

    generateSessions() {
      const result = []

      const base = new Date(
        this.formatDate(this.startDate) + "T" +
        this.formatTime(this.startTime)
      )

      let count = 0
      let cursor = new Date(base)

      while (count < this.sessionCount) {
        if (cursor.getDay() === this.weekday) {
          const local = new Date(cursor)
          const utc = new Date(local.toISOString())

          result.push({
            localDate: local,
            utcDate: utc,
            localLabel: local.toISOString().replace("T", " ").slice(0, 16),
            utcLabel: utc.toISOString().replace("T", " ").slice(0, 16)
          })

          count++
        }

        cursor.setDate(cursor.getDate() + 1)
      }

      return result
    },

    checkTeacher(teacher, session) {
      const dateStr = session.localDate.toISOString().slice(0, 10)
      const hour = session.localDate.getHours()

      // --- AVAILABILITY CHECK ---

      const hasAvailability = teacher.availabilitySlots.some(slot => {
        return (
          slot.weekday === this.weekday &&
          slot.startDate <= dateStr &&
          slot.endDate >= dateStr &&
          parseInt(slot.startTime.split(":")[0]) === hour
        )
      })

      if (!hasAvailability) {
        return {
          teacherId: teacher.id,
          ok: false,
          message: "Outside availability"
        }
      }

      // --- BOOKING CHECK ---

      const isBooked = teacher.bookings.some(b =>
        b.sessions.some(s =>
          s.startDateTime.slice(0, 16) ===
          session.localLabel.replace(" ", "T")
        )
      )

      if (isBooked) {
        return {
          teacherId: teacher.id,
          ok: false,
          message: "Slot already booked"
        }
      }

      return {
        teacherId: teacher.id,
        ok: true,
        message: "Available"
      }
    },

    formatTime(t) {
      return new Date(t).toTimeString().slice(0, 5)
    },

    formatDate(d) {
      return new Date(d).toISOString().slice(0, 10)
    }
  }
}
</script>

<style scoped>
.form-card.wide {
  max-width: 1200px;
}

.checker-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
</style>
