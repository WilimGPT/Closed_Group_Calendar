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
          <el-option v-for="tz in timezones" :key="tz" :label="tz" :value="tz" />
        </el-select>
      </div>
    </div>

    <div class="form-row">
      <label>Group Reference</label>
      <el-input v-model="groupReference" placeholder="Group Name / Reference" />
    </div>

    <el-button type="primary" class="mt-4" @click="runCheck">
      Confirm & Check
    </el-button>

    <!-- RESULT TABLE -->
    <div v-if="results.length" class="mt-6 table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Session ({{ timeZone }} / UTC)</th>
            <th v-for="t in teachers" :key="t.id">{{ t.name }}</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="(row, i) in results" :key="i">
            <td class="session-cell" @click="openEditor(i)">
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

        <tfoot>
          <tr>
            <td><strong>Actions</strong></td>

            <td
              v-for="t in teachers"
              :key="'action-' + t.id"
              class="action-cell"
            >
              <el-button type="primary" size="mini" @click="attemptBooking(t)">
                Book Course
              </el-button>
            </td>
          </tr>
        </tfoot>
      </table>
    </div>

    <!-- EDIT SESSION DIALOG -->
    <el-dialog title="Edit Session" :visible="editingIndex !== null" width="400px">
      <div class="form-row">
        <label>Date</label>
        <el-date-picker v-model="editDate" type="date" />
      </div>

      <div class="form-row">
        <label>Time</label>
        <el-time-picker v-model="editTime" format="HH:mm" />
      </div>

      <div style="margin-top: 20px; text-align: right;">
        <el-button @click="editingIndex = null">Cancel</el-button>
        <el-button type="primary" @click="saveEdit">OK</el-button>
      </div>
    </el-dialog>

    <!-- BOOKING CONFLICT MODAL -->
    <el-dialog
      title="Booking Conflicts Detected"
      :visible.sync="showConflictModal"
      width="400px"
    >
      <p>
        Some sessions conflict with availability or existing bookings.
        Do you want to proceed anyway?
      </p>

      <div style="margin-top: 20px; text-align: right;">
        <el-button @click="showConflictModal = false">Cancel</el-button>
        <el-button type="danger" @click="forceBooking">Confirm Anyway</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import api from "../api"
import timezones from "../timezones"
import { DateTime } from "luxon"

export default {
  data() {
    return {
      language: "english",
      weekday: 1,
      startTime: null,
      startDate: null,
      sessionCount: 5,
      duration: 60,
      timeZone: "Europe/Warsaw",
      groupReference: "",

      teachers: [],
      results: [],
      sessions: [],

      timezones,
      weekdays: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],

      editingIndex: null,
      editDate: null,
      editTime: null,

      pendingTeacher: null,
      showConflictModal: false,
    }
  },

  methods: {
    async runCheck() {
      const res = await api.get(this.language)
      this.teachers = res.data.teachers

      this.sessions = this.generateSessions()
      this.recheckStatuses()
    },

    recheckStatuses() {
      this.results = this.sessions.map(session => {
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
      if (!this.startDate || !this.startTime) return []

      const startISO =
        DateTime.fromJSDate(this.startDate).toISODate() +
        "T" +
        DateTime.fromJSDate(this.startTime).toFormat("HH:mm")

      let cursor = DateTime.fromISO(startISO, { zone: this.timeZone })
      let count = 0

      while (count < this.sessionCount) {
        if ((cursor.weekday % 7) === this.weekday) {
          const local = cursor
          const utc = cursor.toUTC()

          result.push({
            localDateTime: local,
            utcDateTime: utc,
            localLabel: local.toFormat("yyyy-MM-dd HH:mm"),
            utcLabel: utc.toFormat("yyyy-MM-dd HH:mm"),
            isCustom: false
          })

          count++
        }

        cursor = cursor.plus({ days: 1 })
      }

      return result
    },

    //-------------------------------------------------------------------
    //  UPDATED: duration-aware + multiple-weekday availability check
    //-------------------------------------------------------------------
    checkTeacher(teacher, session) {
      const sessionUTC = session.utcDateTime
      const sessionEndUTC = sessionUTC.plus({ minutes: this.duration })

      const hasAvailability = teacher.availabilitySlots.some(slot => {
        const slotLocalMoment = sessionUTC.setZone(slot.timeZone)
        const slotDateISO = slotLocalMoment.toISODate()

        const slotStartLocal = DateTime.fromISO(
          `${slotDateISO}T${slot.startTime}`,
          { zone: slot.timeZone }
        )

        const slotEndLocal = DateTime.fromISO(
          `${slotDateISO}T${slot.endTime}`,
          { zone: slot.timeZone }
        )

        const slotStartUTC = slotStartLocal.toUTC()
        const slotEndUTC = slotEndLocal.toUTC()

        return (
          slot.weekdays.includes(slotLocalMoment.weekday) &&
          sessionUTC >= slotStartUTC &&
          sessionEndUTC <= slotEndUTC &&
          slot.startDate <= slotDateISO &&
          slot.endDate >= slotDateISO
        )
      })

      if (!hasAvailability) {
        return { teacherId: teacher.id, ok: false, message: "Outside availability" }
      }

      const isBooked = teacher.bookings.some(b =>
        b.sessions.some(s => {
          const bookingUTC = DateTime.fromISO(s.startDateTime, { zone: s.timeZone }).toUTC()
          return bookingUTC.equals(session.utcDateTime)
        })
      )

      if (isBooked) {
        return { teacherId: teacher.id, ok: false, message: "Slot already booked" }
      }

      return { teacherId: teacher.id, ok: true, message: "Available" }
    },

    //-------------------------------------------------------------------
    // EDITING SESSIONS
    //-------------------------------------------------------------------
    openEditor(index) {
      const session = this.sessions[index]

      this.editingIndex = index
      this.editDate = session.localDateTime.toJSDate()
      this.editTime = session.localDateTime.toJSDate()
    },

    saveEdit() {
      const session = this.sessions[this.editingIndex]

      const newLocal = DateTime.fromJSDate(this.editDate)
        .set({
          hour: DateTime.fromJSDate(this.editTime).hour,
          minute: DateTime.fromJSDate(this.editTime).minute
        })
        .setZone(this.timeZone)

      const newUTC = newLocal.toUTC()

      session.localDateTime = newLocal
      session.utcDateTime = newUTC
      session.localLabel = newLocal.toFormat("yyyy-MM-dd HH:mm")
      session.utcLabel = newUTC.toFormat("yyyy-MM-dd HH:mm")
      session.isCustom = true

      this.recheckStatuses()
      this.editingIndex = null
    },

    //-------------------------------------------------------------------
    // BOOKING FUNCTIONS
    //-------------------------------------------------------------------
    teacherHasFullAvailability(teacherId) {
      const index = this.teachers.findIndex(t => t.id === teacherId)
      if (index === -1) return false

      return this.results.every(row => row.statuses[index].ok === true)
    },

    attemptBooking(teacher) {
      const fullOK = this.teacherHasFullAvailability(teacher.id)

      if (fullOK) {
        this.commitBooking(teacher)
      } else {
        this.pendingTeacher = teacher
        this.showConflictModal = true
      }
    },

    forceBooking() {
      this.commitBooking(this.pendingTeacher)
      this.showConflictModal = false
      this.pendingTeacher = null
    },

    async commitBooking(teacher) {
      if (!this.groupReference) {
        this.$message.error("Please enter a group reference before booking.")
        return
      }

      const bookingId = `${this.language}_t${teacher.id.split('_t')[1]}_b${Date.now()}`

      const booking = {
        id: bookingId,
        groupReference: this.groupReference,
        sessions: this.sessions.map((s, index) => ({
          id: `${bookingId}_s${index + 1}`,
          startDateTime: s.localDateTime.toISO(),
          durationMinutes: this.duration,
          timeZone: this.timeZone
        }))
      }

      try {
        await api.post(`${this.language}/book/${teacher.id}`, booking)
        this.$message.success("Course booked successfully!")
      } catch (err) {
        console.error(err)
        this.$message.error("Failed to book course.")
      }
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

.session-cell {
  cursor: pointer;
  text-decoration: underline;
}

.session-cell:hover {
  background: #f3f6ff;
}
</style>
