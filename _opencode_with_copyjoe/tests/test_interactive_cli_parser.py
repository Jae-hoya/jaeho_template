from scripts.interactive_copy_chat import ChatState, apply_local_command, parse_user_command


def test_parse_user_command() -> None:
    command, args = parse_user_command('/set product_name "Copyjoe Pro"')
    assert command == "set"
    assert args == ["product_name", "Copyjoe Pro"]


def test_parse_plain_text_as_say() -> None:
    command, args = parse_user_command("클릭률이 떨어진다")
    assert command == "say"
    assert args == ["클릭률이 떨어진다"]


def test_local_command_updates_state() -> None:
    state = ChatState(base_url="http://127.0.0.1:8000")

    apply_local_command(state, "set", ["product_name", "Copyjoe X"])
    assert state.payload["product_name"] == "Copyjoe X"

    before = bool(state.payload["use_rag"])
    apply_local_command(state, "toggle", ["use_rag"])
    assert state.payload["use_rag"] is (not before)

    apply_local_command(state, "style", ["remove", "sns"])
    assert "sns" not in state.payload["styles"]
