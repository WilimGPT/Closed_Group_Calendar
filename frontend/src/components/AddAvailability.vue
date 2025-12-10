<template>
  <div class="form-card">
    <h2>Add Availability</h2>

    <div class="form-row">
      <label>Language</label>
      <el-select v-model="language">
        <el-option label="English" value="english" />
        <el-option label="Spanish" value="spanish" />
        <el-option label="German" value="german" />
      </el-select>
    </div>

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

    <div class="form-row">
      <label>Day of Week</label>
      <el-select v-model="weekday">
        <el-option v-for="(d, i) in weekdays" :key="i" :label="d" :value="i" />
      </el-select>
    </div>

    <div class="form-row-group">
      <div>
        <label>Start Time</label>
        <el-time-picker v-model="startTime" format="HH:mm" />
      </div>
      <div>
        <label>End Time</label>
        <el-time-picker v-model="endTime" format="HH:mm" />
      </div>
    </div>

    <div class="form-row-group">
      <div>
        <label>Start Date</label>
        <el-date-picker v-model="startDate" type="date" />
      </div>
      <div>
        <label>End Date</label>
        <el-date-picker v-model="endDate" type="date" />
      </div>
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

    <el-button type="primary" @click="confirmSlot">
      Confirm
    </el-button>

    <el-button v-if="confirmed" type="success" @click="saveSlot">
      Execute Save
    </el-button>
  </div>
</template>


<script>
import api from "../api"
import timezones from "../timezones"

export default {
  data() {
    return {
      language: "english",
      timezones,
      teachers: [],
      teacherId: "",

      weekday: 1,
      startTime: "",
      endTime: "",
      startDate: "",
      endDate: "",
      timeZone: "Europe/Warsaw",

      confirmed: false,
      slotPayload: null,

      weekdays: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    }
  },

  watch: {
    language() {
      this.loadTeachers()
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
    },

    confirmSlot() {
      const teacher = this.teachers.find(t => t.id === this.teacherId)
      const nextIndex = teacher.availabilitySlots.length + 1

      const slotId = `${this.teacherId}_a${nextIndex}`

      this.slotPayload = {
        id: slotId,
        weekday: this.weekday,
        startTime: this.formatTime(this.startTime),
        endTime: this.formatTime(this.endTime),
        startDate: this.formatDate(this.startDate),
        endDate: this.formatDate(this.endDate),
        timeZone: this.timeZone
      }

      this.confirmed = true
      alert("Slot confirmed. Click Execute Save to persist.")
    },

    async saveSlot() {
      await api.post(`${this.language}/add-availability/`, {
        teacherId: this.teacherId,
        slot: this.slotPayload
      })

      alert("Availability saved to backend.")
      this.confirmed = false
    },

    formatDate(d) {
      return new Date(d).toISOString().slice(0, 10)
    },

    formatTime(t) {
      return new Date(t).toTimeString().slice(0, 5)
    }
  }
}
</script>
