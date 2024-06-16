<script setup>
import { ref } from 'vue'
import { NModal, NCard, NUpload, NButton } from 'naive-ui'
import BaseLoader from '@/components/BaseLoader.vue'
import { useImageStore } from '@/stores/useImageStore'

const isShown = ref(true)

const imageStore = useImageStore()

const handleUpload = async ({ file }) => {
    try {
        imageStore.startLoading()
        imageStore.setImage(file)

        const formData = new FormData()
        formData.append('file', imageStore.image.file)
        const response = await fetch('http://158.160.32.229/detect', {
            method: 'POST',
            body: formData
        })

        const data = await response.json()

        imageStore.setResult(data)
    } finally {
        imageStore.stopLoading()
    }
}
</script>

<template>
    <NModal v-model:show="isShown" :close-on-esc="false" :mask-closable="false">
        <NCard
            style="width: 500px; height: 250px"
            title="Загрузите фотографию для распознавания"
            :bordered="false"
            size="huge"
            role="dialog"
            aria-modal="true"
        >
            <template #header> Загрузите фотографию для распознавания </template>
            <template #default>
                <div class="upload-content">
                    <NUpload class="upload-component" :custom-request="handleUpload">
                        <NButton type="primary" size="large">Выбрать</NButton>
                    </NUpload>
                    <BaseLoader v-if="imageStore.isLoading" />
                </div>
            </template>
        </NCard>
    </NModal>
</template>

<style>
.upload-content {
    display: flex;

    align-items: center;

    justify-content: center;

    height: 100%;
}

.upload-component {
    display: inline-block;

    width: auto;
}

.n-upload-file-list {
    display: none;
}
</style>
