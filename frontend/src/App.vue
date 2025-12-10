<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">
      Scheduler – API Connection Test
    </h1>

    <el-button type="primary" @click="loadEnglish">
      Load English JSON
    </el-button>

    <pre v-if="json" class="mt-6 p-4 bg-gray-100 rounded text-sm">
{{ json }}
    </pre>
  </div>
</template>

<script>
import api from "./api"

export default {
  name: "App",

  data() {
    return {
      json: null
    }
  },

  methods: {
    async loadEnglish() {
      try {
        const res = await api.get("english")
        this.json = res.data
      } catch (err) {
        console.error(err)
        alert("Backend connection failed")
      }
    }
  }
}
</script>

<style>
body {
  margin: 0;
}
</style>
