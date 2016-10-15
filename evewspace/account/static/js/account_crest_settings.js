$(document).ready(function() {
    GetAccountCrestSettingsForm();
});

function GetAccountCrestSettingsForm() {
    $.ajax({
        type: "GET",
        url: "/account/crest/",
        success: function(data){
            $('#accountCrestSettingsHolder').html(data);
        }
    });
}

function SubmitAccountCrestSettings(link) {
	$.ajax({
		type: "GET",
		url: link.href,
		success: function(data){
			$('#accountCrestSettingsHolder').html(data);
		}
	});
}

function SubmitAccountCrestSettingsForm() {
    $.ajax({
        type: "POST",
        data: $('#accountProfSettingsForm').serialize(),
        url: "/account/crest/",
        success: function(data){
            $('#accountCrestSettingsHolder').html(data);
        }
    });
}
