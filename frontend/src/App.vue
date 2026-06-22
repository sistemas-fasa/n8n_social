<script setup>
import { computed, onMounted, ref } from "vue";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const health = ref(null);
const error = ref("");

const backendStatus = computed(() => {
  if (health.value?.status === "ok") {
    return "Backend: conectado";
  }

  if (error.value) {
    return "Backend: sin conexion";
  }

  return "Backend: verificando";
});

onMounted(async () => {
  try {
    const response = await fetch(`${apiBaseUrl}/health`);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    health.value = await response.json();
  } catch (caughtError) {
    error.value = caughtError instanceof Error ? caughtError.message : "Error desconocido";
  }
});
</script>

<template>
  <main class="shell">
    <section class="status-panel">
      <p class="eyebrow">Ferreteria Avenida</p>
      <h1>FASA Social Dashboard</h1>
      <p class="status" :class="{ connected: health?.status === 'ok', disconnected: error }">
        {{ backendStatus }}
      </p>
      <p class="service" v-if="health?.service">Servicio: {{ health.service }}</p>
    </section>
  </main>
</template>
