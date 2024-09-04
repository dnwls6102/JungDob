function pressPostLike(){

    $.ajax({
        type: "POST",
        url: "/api/pressPostLike",
        data: { title: title, content: content, week: week },
        success: function (response) {
          if (response["result"] == "success") {
            alert("업로드 완료");
            location.replace("/main");
          } else if (response["result"] == "noTitle") {
            alert("제목을 입력하세요!");
          } else if (response["result"] == "noContent") {
            alert("내용을 입력하세요!");
          } else alert("서버 오류");
        },
      });
}

function select(id){

    let reply_id = $('#id').val();

    $.ajax({
        type: "POST",
        url: "/api/select",
        data: { post_id : id, reply_id : reply_id},
        success: function(response) {
            if(response['result'] == "success") {
                alert("채택완료")
            }
            else{
                alert("채택불가")
            }
        }
    })

}