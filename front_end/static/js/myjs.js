$(document).ready(function () {
    // 服务器信息配置
    // 外网配置
    //var serverIP = "abstract.ibiter.org";
    //var serverPort = "80";
    // 内网配置
     var serverIP = "10.15.8.75";
     var serverPort = "8080";

    // 定义测试文本
    var textArray = [
        "the palestinian authority officially became the 123rd member of the international criminal court on wednesday , a step that gives the court jurisdiction over alleged crimes in palestinian territories . the formal accession was marked with a ceremony at the hague , in the netherlands , where the court is based . the palestinians signed the icc 's founding rome statute in january , when they also accepted its jurisdiction over alleged crimes committed `` in the occupied palestinian territory , including east jerusalem , since june 13 , 2014 . '' later that month , the icc opened a preliminary examination into the situation in palestinian territories , paving the way for possible war crimes investigations against israelis . as members of the court , palestinians may be subject to counter-charges as well . israel and the united states , neither of which is an icc member , opposed the palestinians ' efforts to join the body . but palestinian foreign minister riad al-malki , speaking at wednesday 's ceremony , said it was a move toward greater justice . `` as palestine formally becomes a state party to the rome statute today , the world is also a step closer to ending a long era of impunity and injustice , '' he said , according to an icc news release . `` indeed , today brings us closer to our shared goals of justice and peace . '' judge kuniko ozaki , a vice president of the icc , said acceding to the treaty was just the first step for the palestinians . `` as the rome statute today enters into force for the state of palestine , palestine acquires all the rights as well as responsibilities that come with being a state party to the statute . these are substantive commitments , which can not be taken lightly , '' she said . rights group human rights watch welcomed the development . `` governments seeking to penalize palestine for joining the icc should immediately end their pressure , and countries that support universal acceptance of the court 's treaty should speak out to welcome its membership , '' said balkees jarrah , international justice counsel for the group . `` what 's objectionable is the attempts to undermine international justice , not palestine 's decision to join a treaty to which over 100 countries around the world are members . '' in january , when the preliminary icc examination was opened , israeli prime minister benjamin netanyahu described it as an outrage , saying the court was overstepping its boundaries . the united states also said it `` strongly '' disagreed with the court 's decision . `` as we have said repeatedly , we do not believe that palestine is a state and therefore we do not believe that it is eligible to join the icc , '' the state department said in a statement . it urged the warring sides to resolve their differences through direct negotiations . `` we will continue to oppose actions against israel at the icc as counterproductive to the cause of peace , '' it said . but the icc begs to differ with the definition of a state for its purposes and refers to the territories as `` palestine . '' while a preliminary examination is not a formal investigation , it allows the court to review evidence and determine whether to investigate suspects on both sides . prosecutor fatou bensouda said her office would `` conduct its analysis in full independence and impartiality . '' the war between israel and hamas militants in gaza last summer left more than 2,000 people dead . the inquiry will include alleged war crimes committed since june . the international criminal court was set up in 2002 to prosecute genocide , crimes against humanity and war crimes . cnn 's vasco cotovio , kareem khadder and faith karimi contributed to this report .",
        "in the second scandal this year involving alleged illegal union donations to the former ruling party , an opposition senator filed a complaint wednesday claiming that money diverted from a rail workers ' union membership fund wound up in the #### campaign of former president ernesto zedillo .",
        "the sri lankan government on wednesday announced the closure of government schools with immediate effect as a military campaign against tamil separatists escalated in the north of the country .",
        "中新网8月1日电 综合报道，当地时间7月31日，美国政府宣布，将伊朗外长扎里夫纳入制裁名单，并宣称美国将继续对伊朗施加最大压力的行动，直至德黑兰放弃其“鲁莽政策”。随后，扎里夫在社交媒体上进行了回应，表示美国对其实施制裁，是认为他对美国议程的造成了威胁。扎里夫称：“美国将我(纳入制裁名单)的原因在于我是伊朗在世界上的主要代表……这不会影响我或我的家人，因为我在伊朗以外没有财产或利益。谢谢你们认为我是对你们议程的重大威胁。”据报道，扎里夫此前曾指责美国在中东政策的失败，并敦促美国总统特朗普对此进行外交努力。他表示，外交道路等同于谨慎，而不是软弱。"
    ];

    $("#modifyBtn").hide();

    // 字符串格式化函数
    String.prototype.format = function () {
        var values = arguments;
        return this.replace(/\{(\d+)\}/g, function (match, index) {
            if (values.length > index) {
                return values[index];
            } else {
                return "";
            }
        });
    };

    // 自适应高度
    $('#text-input').each(function () {
        this.setAttribute('style', 'height:' + (this.scrollHeight) + 'px;overflow-y:hidden;');
    }).on('input focus', function () {
        var length = $("#text-input").val().length;
        $("#wordCountSpan").text(length.toString());
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    $('#text-output').each(function () {
        this.setAttribute('style', 'height:' + (this.scrollHeight) + 'px;overflow-y:hidden;');
    }).on('input focus', function () {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    // 清除文字按钮
    $("#clearTextBtn").click(function () {
        $("#text-input").val("");
        $("#text-input").focus();
    });


    // 语言选择
    $(".langSelect").click(function () {
        $("#lang").text($(this).text());
    });

    // 测试文本选择
    $(".textSelect").click(function () {
        var textId = $(this).attr("id");  // text1
        var id_index = Number(textId.substr(4, 1));
        $("#text-input").val(textArray[id_index - 1]);
        $("#text-input").focus();   // 设置焦点触发textarea自适应函数
    });


    function isChinese(str) {
        return /[^\x00-\xff]/g.test(str);
    }

    // 点击生成摘要
    $("#summarizeBtn").click(function () {

        var lang = $("#lang").text().trim();   // 语言选项
        var srcText = $("#text-input").val();   // 输入的文本内容

        // 判断是否为空
        if (!srcText) {
            // 处理内容为空
        } else {
            // 检测语言类型
            if (lang == "English") {
                lang = "Eng";
            } else if (lang == "中文") {
                lang = "Zh"
            } else {
                // 自动检测
                lang = isChinese(srcText) ? "Zh" : "Eng";
                $("#{0}".format(lang)).click();
            }

            // 清空结果
            $("#modifyBtn").hide();
            $("#text-output").text("");

            // 设置按钮状态与等待loader
            $("#summarizeBtn").attr("disabled", true);    // 设置按钮不可用
            $("#summarizeBtn").tooltip('hide');            // 隐藏tooltips提示
            $("#summarizeBtn").attr("hidden", true);
            $("#loader").attr("hidden", false);

            // 发送ajax请求
            $.post("http://{0}:{1}/as_client.php".format(serverIP, serverPort),
                {
                    src_data: $("#text-input").val(),
                    lang: lang,  // Zh  Eng
                },
                function (data, status) {
                    console.log(status, data);
		    console.log("success-accept");
                    try {
                        jsonData = JSON.parse(data);
                    } catch (e) {
                        console.log(e);
                    }

                    if (status == "success") {
                        if (typeof(jsonData) == 'undefined' && data.trim() == "Connection went wrong: TSocket: Could not connect to 127.0.0.1:5555 (Connection refused [111])") {
                            // 服务器错误
                            $("#serverError").toast("show");
                        } else {
                            // 返回正常结果 标注关键词
                            var abstractText = jsonData['ResponseData'].trim();
                            var keywords = jsonData['string_temp'].split(" ");              // 关键词按空格分割
                            for (let i = 0; i < keywords.length; i++) {
                                if (keywords[i].trim()) {
                                    var re = new RegExp("\\b"+keywords[i]+"\\b","gim");
                                    console.log(re);
                                    abstractText = abstractText.replace(re, "<span class='text-primary'>" + keywords[i] + "</span>");
                                }
                            }

                            // 修改内容上传服务器
                            $("#modifyBtn").show();
                            $("#modifyBtn").attr("hidden", false);

                            $("#text-output").text("");
                            $("#text-output").append(abstractText);        // 显示结果
                            $("#text-output").focus();


                        }
                    } else {
                        // 连接失败
                        $("#connectError").toast("show");
                    }
                    $("#summarizeBtn").attr("disabled", false);    // 设置按钮可用
                    $("#summarizeBtn").attr("hidden", false);
                    $("#loader").attr("hidden", true);
                });
        }
    });


    // 修改结果并上传服务器
    $("#modifyBtn").click(function () {
        var text = $("#modifyBtn").text();
        if (text == "修改建议") {
            $("#modifyBtn").text("保存修改");
            $("#text-output").attr("readonly", false);
            $("#text-output").attr("contenteditable", true);
        } else {
            $("#modifySuccess").toast("show");
            $("#modifyBtn").text("修改建议");
            $("#text-output").attr("contenteditable", false);
            $("#text-output").attr("readonly", true);
        }
    });


});
