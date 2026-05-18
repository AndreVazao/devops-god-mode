from app.brain.god_brain import think
import os

def test_pipeline_routing():
    # Mocking environment for standalone run if needed
    os.environ["RELAY_URL"] = "https://devops-god-mode.vercel.app/api"
    os.environ["RELAY_TOKEN"] = "GODMODE_SECURE_TOKEN"
    os.environ["GODMODE_ENV"] = "dev"

    print("Testing 'criar' trigger...")
    res = think("criar uma nova api de pagamentos")
    print("Result:", res)
    assert res.get("distributed") is True
    assert "goal" in res

    print("Testing 'deploy' trigger...")
    res = think("deploy para vercel")
    print("Result text summary:", res.get("text", "")[:100])
    # Pipeline returns a message structure.
    # We accept both success and failure (blocked by tests) as "routing success"
    # as long as it hit the pipeline logic.
    assert "text" in res
    assert ("Pipeline Enterprise completo" in res["text"] or "Bloqueado: testes falharam" in res["text"])

    print("Testing regular goal...")
    res = think("olá")
    print("Result:", res)
    assert "goal" in res

if __name__ == "__main__":
    try:
        test_pipeline_routing()
        print("✅ Enterprise Pipeline routing test passed!")
    except Exception as e:
        print(f"❌ Enterprise Pipeline routing test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
