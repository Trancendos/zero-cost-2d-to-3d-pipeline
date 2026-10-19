import json,os,struct,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from hardware_gate import select_gpu
from local_llm_rig_assist import DEFAULT,clamp,safe_base
from rig_with_skintokens import validate_glb

class RigContracts(unittest.TestCase):
 def setUp(self):
  self.info={"available":True,"gpus":[{"index":0,"uuid":"GPU-a","name":"A","total_mb":16000,"free_mb":4000},{"index":1,"uuid":"GPU-b","name":"B","total_mb":24000,"free_mb":18000}]}
 def test_selects_gpu_with_free_memory(self):
  ok,_,gpu=select_gpu(self.info,visible="")
  self.assertFalse(ok)
  ok,_,gpu=select_gpu(self.info)
  self.assertTrue(ok); self.assertEqual(gpu["index"],1)
 def test_respects_selected_gpu(self):
  ok,_,gpu=select_gpu(self.info,visible="0")
  self.assertFalse(ok); self.assertEqual(gpu["index"],0)
 def test_llm_output_is_bounded_and_unknown_keys_ignored(self):
  got=clamp({"top_k":999,"top_p":0.9,"temperature":1.1,"num_beams":3,"command":"do bad"})
  self.assertEqual(got["top_k"],DEFAULT["top_k"]); self.assertNotIn("command",got)
 def test_non_loopback_llm_is_rejected(self):
  with self.assertRaises(ValueError): safe_base("http://example.com:11434")
 def test_glb_without_skin_is_rejected(self):
  doc={"asset":{"version":"2.0"},"nodes":[],"skins":[]}; raw=json.dumps(doc).encode(); raw+=b" " *((4-len(raw)%4)%4)
  payload=b"glTF"+struct.pack("<II",2,20+len(raw))+struct.pack("<II",len(raw),0x4E4F534A)+raw
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"bad.glb"; p.write_bytes(payload)
   with self.assertRaisesRegex(ValueError,"no skin"): validate_glb(p)
if __name__=="__main__": unittest.main()
