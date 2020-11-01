$(document).ready(function () {
  $("#addReview").on("submit", function (event) {
    event.preventDefault();
    $("#reviewModal").modal('hide')
    $("html, body").animate({ scrollTop: 0 }, "fast");
    document.getElementById("msg-box-ajax").style.display = "block";
    $.ajax({
      data: {
        reviewCompanyName: $("#reviewCompanyName").val(),
        rounds: $("#noOfRounds").val(),
        reviewRole: $("#reviewRole").val(),
        reviewRecruitType: $("#reviewRecruitType").val(),
        details: editor.root.innerHTML,
        difficultyLevel: $("#difficultyScore").val(),
        experienceLevel: $("#interviewingScore").val(),
      },
      type: "POST",
      url: "/addReview",
    }).done(function (data) {
      if (data.error) {
        document.getElementById("msg-box-ajax").style.display = "block";
        document.getElementById("ajax-response").innerHTML = data.error;
      } else {
        document.getElementById("msg-box-ajax").style.display = "block";
        document.getElementById("ajax-response").innerHTML = data.success;
      }
    });
  });

  var scroller = document.querySelector("#review-contents");
  var template = document.querySelector("#review-card-template");
  var sentinel = document.querySelector("#sentinel");
  function loadItems() {
    // Use fetch to request data and pass the counter value in the QS
    fetch("/getreviews").then((response) => {
      // Convert the response data to JSON
      response.json().then((data) => {
        // If empty JSON, exit the function
        if (!data.length) {
          // Replace the spinner with "No more posts"
          sentinel.innerHTML = "You're all set for today! 🥳";
          return;
        }
        // Iterate over the items in the response
        for (var i = 0; i < data.length; i++) {
          console.log(i)
          // Clone the HTML template
          let template_clone = template.content.cloneNode(true);

          // Query & update the template content
		  template_clone.querySelector("#card-company").innerHTML = `${data[i][2]}`;
		  template_clone.querySelector("#card-position").innerHTML = `${data[i][1]}`;
		  template_clone.querySelector("#card-contrib-by").innerHTML = `${data[i][0]}`;
		  template_clone.querySelector("#company-logo-disp").src = `${data[i][4]}`;
      template_clone.querySelector("#card-batch").innerHTML = `${data[i][3]}`.substring(0,16);
      template_clone.querySelector("#ivRating").innerHTML = `${data[i][6]}`+"⭐";
      template_clone.querySelector("#ovRating").innerHTML = `${data[i][7]}`+"⭐" ;
      template_clone.querySelector("#review-card-template-unique").id = `${data[i][5]}`; 
      template_clone.querySelector("#review-card-anchor").setAttribute("href",`/viewexperience/${data[i][5]}` ) ;
      
          // Append template to dom
          scroller.appendChild(template_clone);
        }
      });
    });
  }

  // Create a new IntersectionObserver instance
  var intersectionObserver = new IntersectionObserver((entries) => {
    // Uncomment below to see the entry.intersectionRatio when
    // the sentinel comes into view

    // entries.forEach(entry => {
    //   console.log(entry.intersectionRatio);
    // })

    // If intersectionRatio is 0, the sentinel is out of view
    // and we don't need to do anything. Exit the function
    if (entries[0].intersectionRatio <= 0) {
      return;
    }

    // Call the loadItems function
    loadItems();
  });

  // Instruct the IntersectionObserver to watch the sentinel
  intersectionObserver.observe(sentinel);
});



function hide_msg() {
  document.getElementById("msg-box").style.display = "none";
  console.log("sdsd");
}

function hide_msg_ajax() {
  document.getElementById("msg-box-ajax").style.display = "none";
  console.log("sdsd");
}

if ($(window).width() > 200) {
  $(window).scroll(function () {
    if ($(this).scrollTop() > 40) {
      $("#subnav").addClass("fixed-top");
      // add padding top to show content behind navbar
      $("#subnav").css("margin-top", "0");
      $("body").css("padding-top", $(".navbar").outerHeight() + "px");
    } else {
      $("#subnav").removeClass("fixed-top");
      $("#subnav").css("margin-top", "8px");
      // remove padding top from body
      $("body").css("padding-top", "0");
    }
  });
}

var uploadField = document.getElementById("company-logo");

uploadField.onchange = function () {
  if (this.files[0].size > 1297152) {
    alert("Image is too big! Please upload image of size less than 1mb.");
    this.value = "";
  }
};
