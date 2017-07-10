
    $( document ).ready(function() {
        $("input[type=checkbox]")
        .each(function() {
            if (this.name.indexOf('txt_checkbox_')!=-1 && this.checked)
            {
                this.click();
                this.click();
            }
        })
    });

    function display_hide_div_child(id_div_child,id_statut_bouton)
    {
        var div_child = document.getElementById(id_div_child);
        var statut_bouton = document.getElementById(id_statut_bouton);
             if(statut_bouton.value == "OK" && (div_child.style.display!="none") )
             {
                div_child.style.display = "none";
             }else
             {
                div_child.style.display = "BLOCK";
             }
    }

    function block_div(check_box,id_div_kinsman,id_statut_bouton,id_div_child)
    {
        var statut_bouton = document.getElementById(id_statut_bouton);
        var div_kinsman= document.getElementById(id_div_kinsman);
        var div_child = document.getElementById(id_div_child);
        if (check_box.checked)
        {
            div_child.style.display = "block";
            statut_bouton.value ="KO";
        }
    }
