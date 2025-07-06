const form = document.getElementById('uploadForm');
const progressBar = document.getElementById('progressBar');
const progressBox = document.getElementById('progressBox');

form.addEventListener('submit', function (e) {
    e.preventDefault();
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    progressBox.style.display = 'block';

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/upload', true);

    xhr.upload.onprogress = function (e) {
        if (e.lengthComputable) {
            const percent = (e.loaded / e.total) * 100;
            progressBar.style.width = percent + '%';
        }
    };

    xhr.onload = function () {
        if (xhr.status === 200) {
            alert('Upload complete!');
            location.reload();
        } else {
            alert('Upload failed!');
        }
    };

    xhr.send(formData);
});
