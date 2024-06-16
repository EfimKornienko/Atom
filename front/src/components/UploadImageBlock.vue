<script setup>
import { ref } from 'vue'
import { NUpload, NUploadDragger, NIcon, NText } from 'naive-ui'
import { ArchiveOutline as ArchiveIcon, EyeOutline as EyeIcon } from '@vicons/ionicons5'
import BaseLoader from '@/components/BaseLoader.vue'
import { useImageStore } from '@/stores/useImageStore'
import JSZip from 'jszip'

const emit = defineEmits(['image-uploaded', 'fill-image'])

const imageStore = useImageStore()

function isImageFile(fileName) {
    const extension = fileName.split('.').pop().toLowerCase()
    return ['jpg', 'jpeg', 'png', 'gif', 'bmp'].includes(extension)
}

const handleUpload = async (imgdata) => {
    try {
        const file = imgdata.file
        imageStore.startLoading()

        if (file.type.includes('rar') || file.type.includes('zip')) {
            const new_zip = new JSZip()
            new_zip.loadAsync(file.file).then(function (zip) {
                imageStore.setZip(
                    zip.filter(
                        (_, zipEntry) =>
                            isImageFile(zipEntry.name) && !zipEntry.name.includes('MACOSX')
                    ), new_zip
                )
            })
        } else {
            imageStore.setImage(file)
            emit('fill-image', file)
        }

        const formData = new FormData()
        formData.append('file', file.file)
        const response = await fetch('http://158.160.32.229/detect', {
            method: 'POST',
            body: formData
        })

        const data = await response.json()

        data.objects.forEach((obj) => (obj.visible = true))

        emit('image-uploaded')
        imageStore.setResult(data)
    } finally {
        imageStore.stopLoading()
    }
}
</script>

<template>
    <div class="upload-content">
        <NUpload v-if="!imageStore.imageURL" :custom-request="handleUpload" style="height: 640px">
            <NUploadDragger
                style="
                    display: flex;

                    flex-direction: column;

                    justify-content: center;

                    height: 640px;
                "
            >
                <div style="margin-bottom: 12px">
                    <NIcon size="48" :depth="3">
                        <ArchiveIcon />
                    </NIcon>
                </div>
                <NText style="font-size: 16px"> Нажмите или перетащите файл для загрузки </NText>
            </NUploadDragger>
        </NUpload>
        <BaseLoader v-if="imageStore.isLoading" />
    </div>
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
