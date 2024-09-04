function upload_post() {
    let title = $('#titleArea').val()
    let content = $('#contentArea').val()

    $.ajax({
        type: "POST",
        url: "/api/createPost",
        data: {post_title : title, post_content : content},
        success: function(response) {
            if (response['result'] == 'success') {
                alert("업로드 완료")
                location.replace('/main')
            }
            else if (response['result'] == 'noTitle') {
                alert("제목을 입력하세요!")
            }
            else if (response['result'] == 'noContent') {
                alert("내용을 입력하세요!")
            }
            else(
                alert("서버 오류")
            )
        }
    })
}