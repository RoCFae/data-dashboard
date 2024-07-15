<template>
  <div class="upload-container">
    <label for="file-upload" class="custom-file-upload">
      Select File
    </label>
    <input id="file-upload" type="file" @change="uploadFile" />
  </div>
</template>

<script>
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000'; // URL base do backend

export default {
  name: 'UploadComponent',
  methods: {
    async uploadFile(event) {
      const file = event.target.files[0];
      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });

        if (response.status === 200) {
          this.$emit('file-uploaded');
        }
      } catch (error) {
        console.error("There was an error uploading the file!", error);
      }
    }
  }
};
</script>

<style scoped>
.upload-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.custom-file-upload {
  display: inline-block;
  padding: 10px 20px;
  cursor: pointer;
  background-color: #1B4242;
  color: #FAF0E6;
  border-radius: 5px;
  border: 2px solid #5C8374;
  transition: background-color 0.3s, color 0.3s;
}

.custom-file-upload:hover {
  background-color: #5C8374;
  color: #092635;
}

input[type="file"] {
  display: none;
}
</style>
