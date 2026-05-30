"""All config files parse, declare a valid base model, and use DoRA + NEFTune."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

CONFIGS_DIR = Path(__file__).resolve().parents[1] / "configs"


def _all_sft_configs():
    return sorted(p for p in CONFIGS_DIR.glob("sft_*.yaml"))


def test_configs_dir_exists():
    assert CONFIGS_DIR.exists() and CONFIGS_DIR.is_dir()


def test_all_sft_configs_load():
    configs = _all_sft_configs()
    assert len(configs) >= 6, f"expected at least 6 SFT configs, got {configs}"
    for c in configs:
        data = yaml.safe_load(c.read_text())
        assert "model" in data and "base_model" in data["model"], c
        assert "training" in data and "output_dir" in data["training"], c


# New-frontier configs that must use the modern PEFT (DoRA) + NEFTune defaults.
# Legacy configs (Qwen 3.5, R1-Distill-32B, V4-Flash, Llama 4 Scout) are kept on
# the older `lora:` schema for backwards compatibility; the SFT script
# accepts both.
_MODERN_CONFIGS = {
    "sft_gemma_4_31b.yaml",
    "sft_gemma_4_e4b.yaml",
    "sft_qwen3_6_27b.yaml",
    "sft_glm_5_1.yaml",
    "sft_kimi_k2_6.yaml",
    "sft_deepseek_v4_pro.yaml",
}


@pytest.mark.parametrize("config_path", _all_sft_configs())
def test_sft_config_uses_modern_peft(config_path: Path):
    """Modern (May 2026) configs use DoRA. Legacy configs may still use LoRA."""
    if config_path.name not in _MODERN_CONFIGS:
        return
    cfg = yaml.safe_load(config_path.read_text())
    peft = cfg.get("peft", {})
    assert peft, f"{config_path.name}: missing `peft:` block"
    assert peft.get("method") == "dora", \
        f"{config_path.name}: peft.method should be 'dora' (modern default)"


@pytest.mark.parametrize("config_path", _all_sft_configs())
def test_sft_config_enables_neftune(config_path: Path):
    if config_path.name not in _MODERN_CONFIGS:
        return
    cfg = yaml.safe_load(config_path.read_text())
    neftune = cfg.get("neftune", {})
    assert neftune.get("enabled") is True, \
        f"{config_path.name}: neftune should be enabled (free quality boost)"


def test_default_base_model_is_gemma_4_31b():
    """Makefile default should target Gemma 4 31B Dense."""
    makefile = (CONFIGS_DIR.parent / "Makefile").read_text()
    assert "configs/sft_gemma_4_31b.yaml" in makefile, \
        "Makefile default CONFIG should be sft_gemma_4_31b.yaml"


def test_frontier_moe_configs_use_attention_only_lora():
    """MoE bases (GLM-5.1, Kimi K2.6, DeepSeek V4) should use attention-only
    target_modules to avoid the per-expert LoRA explosion."""
    moe_configs = [
        "sft_glm_5_1.yaml",
        "sft_kimi_k2_6.yaml",
        "sft_deepseek_v4_pro.yaml",
        "sft_deepseek_v4_flash.yaml",
    ]
    for name in moe_configs:
        p = CONFIGS_DIR / name
        if not p.exists():
            continue
        cfg = yaml.safe_load(p.read_text())
        peft_cfg = cfg.get("peft") or cfg.get("lora", {})
        targets = peft_cfg.get("target_modules", [])
        mlp_modules = {"gate_proj", "up_proj", "down_proj"}
        overlap = mlp_modules.intersection(set(targets))
        assert not overlap, (
            f"{name}: MoE base should use attention-only LoRA "
            f"(targeting {overlap} replicates the adapter per expert per layer)"
        )
