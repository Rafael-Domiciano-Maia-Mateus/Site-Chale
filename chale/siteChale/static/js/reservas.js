$(document).ready(function () {
    $('#id_chale').change(function () {
        let chaleId = $(this).val();
        let qtdPessoasSelect = $('#id_qtd_pessoas');

        if (!chaleId) {
            qtdPessoasSelect.html('<option value="">--- Selecione um chalé ---</option>');
            return;
        }

        $.ajax({
            url: '/obter_max_pessoas/',
            data: {
                chale_id: chaleId,
            },
            dataType: 'json',
            success: function (data) {
                qtdPessoasSelect.empty();
                qtdPessoasSelect.append('<option value="">--- Selecione ---</option>');
                for (let i = 1; i <= data.max_pessoas; i++) {
                    qtdPessoasSelect.append(`<option value="${i}">${i}</option>`);
                }
            },
            error: function () {
                qtdPessoasSelect.html('<option value="">Erro ao carregar</option>');
            },
        });
    });
});
