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
            var stream_name = $("#stream_name").attr("data-name");
            this.url = "/view_one?stream=" + stream_name;
            event.preventDefault();
            event.stopPropagation();
            dzClosure.processQueue();
        });

        this.on("sending", function(data, xhr, formData) {
            formData.append("action", "upload");
            formData.append("loaded", $("#loaded_image").attr("data-name"));
            formData.append("counts", this.files.length);
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
    }
};
