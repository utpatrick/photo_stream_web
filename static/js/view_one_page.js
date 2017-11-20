Dropzone.options.uploader = {
    autoProcessQueue: false,
    uploadMultiple: true,
    parallelUploads: 100,
    addRemoveLinks: true,
    acceptedFiles: 'image/*',
    paramName: 'image',
    maxFiles: 100,
    url: "#",
    
    init: function () {
        var dzClosure = this;
        $("#submit_btn").click(function (event) {
            event.preventDefault();
            event.stopPropagation();
            dzClosure.processQueue();
        });

        this.on("processing", function (file) {
            this.options.url = $("#upload_url").attr("data-name");
        });

        this.on("sending", function(data, xhr, formData) {
            formData.append("stream", $("#stream_name").attr("data-name"));
            if($("#loaded_image").attr("data-name")) {
                formData.append("loaded", $("#loaded_image").attr("data-name"));
            }
            formData.append("counts", this.files.length);
            formData.append("action", "upload");
            for (var i = 0; i < this.files.length; i++) {
                formData.append("title[" + i + "]", this.files[i].name);
            }
        });
        

        $("#reset_btn").click(function () {
            dzClosure.removeAllFiles();
        })
    },
    success: function () {
        this.removeAllFiles();
        location.reload();
    }
};
