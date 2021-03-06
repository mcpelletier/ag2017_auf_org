/**
 * Created by benselme on 23/09/16.
 */


$(function () {
    var form = $('.valider-payer-form');
    form.find('input').removeAttr('disabled');
    function disable_paypal_button() {
        form.find('input').attr('disabled', 'disabled')
            .css('background-color', '#DDDDDD')
            .css('font-color', '#AAAAAA');
    }

    form.ajaxForm({
        beforeSubmit: disable_paypal_button,
        success: go_to_paypal
    })
});

function go_to_paypal(responseText, statusText, xhr) {
    if (xhr.status === 200) {
        var form = $('#paypal-form');
        form.find('[name="invoice"]').val(responseText);
        var cancel_field = form.find('[name="cancel_return"]');
        var cancel_url = cancel_field.val().replace('__invoice_uid__',
            responseText);
        cancel_field.val(cancel_url);
        form.submit();
    } else {
        window.location = '/inscription/'
    }


}
