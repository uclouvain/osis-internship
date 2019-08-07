function showEditButton(id){
    $(`#edit-${id}`).show();
}

function hideEditButton(id){
    $(`#edit-${id}`).hide();
}

function buildScoreInput(score_value) {
    let input = document.createElement("input");
    Object.assign(input, {
        value: parseFloat(score_value.replace(',', '.')),
        type: 'number',
        step: 'any',
        min: 0,
        max: 20
    });
    input.style.width = "80px";
    input.classList.add("form-control");
    return input;
}

function buildScoreFormGroup(input) {
    let formGroup = document.createElement("div");
    formGroup.classList.add("input-group", "input-group-sm");
    formGroup.append(input);
    return formGroup;
}

function buildGroupButton() {
    let groupButton = document.createElement("span");
    groupButton.classList.add("input-group-btn");
    return groupButton;
}

function buildConfirmButton(input, cell, data) {
    let confirmButton = document.createElement("button");
    confirmButton.innerHTML = "<icon class='glyphicon glyphicon-ok'><icon/>";
    confirmButton.classList.add("btn", "btn-primary");
    confirmButton.addEventListener('click', () => {
        value = parseFloat(input.value.replace(',', '.'));
        saveScore({'edited': value, 'computed': data.computedScore}, data.student, data.period, cell);
    });
    return confirmButton;
}

function buildCancelButton(cell, oldCellContent) {
    let cancelButton = document.createElement("button");
    cancelButton.innerHTML = "<icon class='glyphicon glyphicon-remove'><icon/>";
    cancelButton.classList.add("btn", "btn-secondary");
    cancelButton.addEventListener('click', () => {
        cell.innerHTML = oldCellContent;
        resetPadding(cell);
    });
    return cancelButton;
}

function buildScoreGroupButton(input, cell, oldCellContent, data) {
    let groupButton = buildGroupButton();
    let confirmButton = buildConfirmButton(input, cell, data);
    let cancelButton = buildCancelButton(cell, oldCellContent);
    groupButton.append(confirmButton);
    groupButton.append(cancelButton);
    return groupButton;
}

function adaptPadding(cell) {
    let paddingTop = parseInt($(cell).css('padding')) / 2 - 1;
    $(cell).css('padding', paddingTop + 'px 0px 0px 0px');
}

function resetPadding(cell){
    $(cell).css('padding', '');
}

function editScore(e){
    let data = {
        student: e.dataset.student,
        period: e.dataset.period,
        computedScore: parseFloat(e.dataset.computed.replace(',', '.'))
    };
    let cell =  $(e).closest('td')[0];
    adaptPadding(cell);
    let oldCellContent = cell.innerHTML;
    const score_value = cell.innerText;
    let input = buildScoreInput(score_value);
    let formGroup = buildScoreFormGroup(input);
    let groupButton = buildScoreGroupButton(input, cell, oldCellContent, data);
    formGroup.append(groupButton);
    cell.innerHTML = "";
    cell.append(formGroup);
    return false;
}

$(document).on('click', '[data-target="#delete_score"]', function(){
    let deleteScoreBtn = $("#delete_score_btn");
    deleteScoreBtn.data(this.dataset);
    deleteScoreBtn.data("cell", $(this).closest('td')[0]);
    return false;
});

function showErrorTooltip(cell, data) {
    let inputGroup = $(cell).find(".input-group")[0];
    inputGroup.classList.add("has-error");
    inputGroup.setAttribute("data-toggle", "tooltip");
    inputGroup.setAttribute("data-placement", "top");
    inputGroup.setAttribute("title", data.responseJSON.error);
    $(inputGroup).tooltip('show');
}

function saveScore(values, student, period, cell) {
    //period undefined means that we are dealing with an evolution score
    let url = period ? "ajax/save_score/" : "ajax/save_evolution_score/";
    let periods_scores = $(`#evolution_score_${student}`).data('scores');
    $.ajax({
        url: url,
        method: "POST",
        data: {
            'value': values.edited,
            'computed': values.computed,
            'student': student,
            'period': period
        },
        success: response => {
            if(period){
                cell.innerHTML = response;
                resetPadding(cell);
                refreshEvolutionScore(student, period, values.edited, periods_scores);
            } else {
                cell.closest('tr').innerHTML = response;
            }
        },
        error: data => {
            showErrorTooltip(cell, data);
        }
    });
}

function deleteScore(e){
    cell = $(e).data('cell');
    student = $(e).data('student');
    period = $(e).data('period');
    computed = parseFloat($(e).data('computed').replace(',', '.'));
    $.ajax({
        url: "ajax/delete_score/",
        method: "POST",
        data: {
            'computed': computed,
            'student': student,
            'period': period
        },
        success: response => {
            cell.innerHTML = response;
            refreshEvolutionScore(student, period, computed);
        },
        error: data => {
            let inputGroup = $(cell).find(".input-group")[0];
            inputGroup.classList.add("has-error");
            inputGroup.setAttribute("data-toggle", "tooltip");
            inputGroup.setAttribute("data-placement", "top");
            inputGroup.setAttribute("title", data.responseJSON.error);
            $(inputGroup).tooltip('show');
        }
    });
}

function refreshEvolutionScore(student_id, period, value, scores){
    let student_evolution_score = $(`#evolution_score_${student_id}`);
    let student_evolution_score_info = $(`#evolution_score_info_${student_id}`);
    scores = student_evolution_score.data('scores') ? student_evolution_score.data('scores') : scores;
    $.ajax({
        url: "ajax/refresh_evolution_score/",
        method: "POST",
        data: {
            'scores': scores,
            'period': period,
            'value': value
        },
        success: response => {
            let evolution_score = response['evolution_score'].toFixed(2).replace('.',',')
            student_evolution_score.data('scores', response['updated_scores']);
            if(!student_evolution_score.data('edited')){
                student_evolution_score[0].innerHTML = evolution_score;
            } else {
                student_evolution_score_info.attr('title', response['computed_title_text']+evolution_score);
            }
        }
    })
}