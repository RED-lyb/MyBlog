<script setup>
import {ref} from 'vue'
import {useStore} from '../stores/counter.js'
import axios from 'axios'
const stores = useStore()
const data = ref("")
const status = ref("")
const apiUrl = import.meta.env.VITE_API_URL
axios.get(apiUrl).then(res => { 
    data.value = res.data
    status.value = res.status
})

</script>
<template>
    <h1>目前正处于测试部署状态，还未正式部署相关内容</h1>
    <p>测试后端返回的信息：data:{{data}},status:{{status}}</p>
</template>