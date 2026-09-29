"""Run: python -m unittest discover -s tests -v

Scenario expectations are written independently from the rule definitions.
The runner also saves the observed case results for report reproducibility.
"""
import json
import platform
import threading
import unittest
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from http.server import ThreadingHTTPServer

from app import Handler
from engine import infer
from knowledge_base import RULES, SOURCES

CASES = [
    ("T01", "Dry mix and wilting", {"soil":"dry","wilting":"yes"}, ["R01"]),
    ("T02", "Wet mix and yellowing", {"soil":"wet","yellowing":"yes"}, ["R02"]),
    ("T03", "Water retained in saucer", {"standing_water":"yes"}, ["R03"]),
    ("T04", "Salt crust and brown tips", {"salt_crust":"yes","brown_tips":"yes"}, ["R04"]),
    ("T05", "Chemically softened water", {"softened_water":"yes"}, ["R05"]),
    ("T06", "Stretched growth in dim light", {"stretched":"yes","low_light":"yes"}, ["R06"]),
    ("T07", "Bleaching after stronger sun", {"bleached":"yes","stronger_sun":"yes"}, ["R07"]),
    ("T08", "Blackening after cold exposure", {"blackening":"yes","cold_exposure":"yes"}, ["R08"]),
    ("T09", "Grey fuzzy growth", {"gray_fuzz":"yes"}, ["R09"]),
    ("T10", "Wilting and dark soft roots", {"wilting":"yes","dark_soft_roots":"yes"}, ["R10"]),
    ("T11", "White powdery leaf growth", {"white_powder":"yes"}, ["R11"]),
    ("T12", "Brown spots with target rings", {"brown_spots":"yes","target_rings":"yes"}, ["R12"]),
    ("T13", "Water-soaked spots with ooze", {"water_soaked":"yes","spot_ooze":"yes"}, ["R13"]),
    ("T14", "Pear-shaped insects", {"pear_insects":"yes"}, ["R14","R20"]),
    ("T15", "Cottony insects", {"cotton_insects":"yes"}, ["R15","R20"]),
    ("T16", "Speckles with fine webbing", {"pale_speckles":"yes","fine_webbing":"yes"}, ["R16","R20"]),
    ("T17", "Attached shell-like bumps", {"shell_bumps":"yes"}, ["R17","R20"]),
    ("T18", "Disturbed tiny white flies", {"white_flies":"yes"}, ["R18","R20"]),
    ("T19", "Dark flies above wet soil", {"dark_flies":"yes","soil":"wet"}, ["R19","R20"]),
    ("T20", "Two pests share one isolation action", {"pear_insects":"yes","cotton_insects":"yes"}, ["R14","R15","R20"]),
    ("T21", "All answers omitted", {}, []),
    ("T22", "Webbing with speckles unknown", {"fine_webbing":"yes","pale_speckles":"unknown"}, []),
    ("T23", "Webbing with speckles absent", {"fine_webbing":"yes","pale_speckles":"no"}, []),
    ("T24", "Wilting but soil not checked", {"wilting":"yes"}, []),
    ("T25", "Wet mix and wilt OR branch", {"soil":"wet","wilting":"yes"}, ["R02"]),
    ("T26", "Black dots OR branch", {"brown_spots":"yes","black_dots":"yes"}, ["R12"]),
    ("T27", "Brown spots alone", {"brown_spots":"yes"}, []),
    ("T28", "Salt crust without brown tips", {"salt_crust":"yes","brown_tips":"no"}, []),
    ("T29", "Dark flies but dry mix", {"dark_flies":"yes","soil":"dry"}, []),
    ("T30", "Wet stress and root rot overlap", {"soil":"wet","wilting":"yes","dark_soft_roots":"yes"}, ["R02","R10"]),
]

OBSERVED = []

def tearDownModule():
    target = Path(__file__).resolve().parents[1] / "test_results.json"
    target.write_text(json.dumps({"run_at":datetime.now(timezone.utc).isoformat(),"python":platform.python_version(),
        "platform":platform.system(),"results":OBSERVED}, indent=2), encoding="utf-8")


class RuleScenarios(unittest.TestCase):
    pass


def make_scenario(case):
    def test(self):
        identifier, name, inputs, expected = case
        result = infer(inputs)
        actual = [x["rule_id"] for x in result["trace"]]
        OBSERVED.append({"id":identifier,"name":name,"inputs":inputs,"expected":expected,"actual":actual,
                         "pass":actual==expected,"status":result["status"],"rounds":result["rounds"]})
        self.assertEqual(actual, expected)
        if "R20" in expected:
            self.assertEqual(result["trace"][-1]["round"],2)
        if not expected:
            self.assertNotIn("healthy", result["status"])
    return test


for case in CASES:
    setattr(RuleScenarios, "test_" + case[0], make_scenario(case))


class EngineProperties(unittest.TestCase):
    def test_unknown_and_no_remain_distinct(self):
        self.assertEqual(infer({})["facts"]["wilting"], "unknown")
        self.assertEqual(infer({"wilting":"no"})["facts"]["wilting"], "no")

    def test_user_cannot_inject_derived_fact(self):
        with self.assertRaises(ValueError): infer({"pest_suspected":True})

    def test_invalid_inputs(self):
        for value in ([], None, {"soil":"flooded"}, {"wilting":True}, {"unknown_key":"yes"}):
            with self.subTest(value=value), self.assertRaises(ValueError): infer(value)

    def test_independent_consultations(self):
        infer({"pear_insects":"yes"})
        self.assertEqual(infer({})["trace"], [])

    def test_inputs_not_mutated(self):
        answers={"pear_insects":"yes"}; infer(answers)
        self.assertEqual(answers,{"pear_insects":"yes"})

    def test_rounds_and_parent_trace(self):
        result=infer({"pear_insects":"yes","cotton_insects":"yes"})
        self.assertEqual(result["rounds"],2)
        self.assertEqual(result["trace"][-1]["parents"],["R14","R15"])
        self.assertEqual(len([x for x in result["trace"] if x["rule_id"]=="R20"]),1)

    def test_rule_order_does_not_prevent_chain(self):
        import engine
        original=engine.RULES
        try:
            engine.RULES=list(reversed(original))
            result=engine.infer({"pale_speckles":"yes","fine_webbing":"yes"})
            self.assertEqual([x["rule_id"] for x in result["trace"]],["R16","R20"])
            self.assertEqual(result["rounds"],2)
        finally: engine.RULES=original

    def test_rule_coverage_and_references(self):
        covered={r for _,_,_,expected in CASES for r in expected}
        self.assertEqual(len(RULES),20)
        self.assertEqual(covered,{r["id"] for r in RULES})
        self.assertTrue(all(r["source_section"] and all(s in SOURCES for s in r["sources"]) for r in RULES))


class HTTPIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(("127.0.0.1",0),Handler)
        cls.worker=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.worker.start()
        cls.base=f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.worker.join()

    def request(self,path,data=None,content_type="application/json"):
        req=Request(self.base+path,data=data,headers={"Content-Type":content_type})
        try:
            with urlopen(req,timeout=3) as response:return response.status,response.read()
        except HTTPError as error:return error.code,error.read()

    def test_home_and_config(self):
        code,body=self.request("/");self.assertEqual(code,200);self.assertIn(b"PlantCare",body)
        code,body=self.request("/api/config");self.assertEqual(len(json.loads(body)["rules"]),20)

    def test_real_inference_endpoint(self):
        code,body=self.request("/api/diagnose",json.dumps({"answers":{"pear_insects":"yes"}}).encode())
        self.assertEqual(code,200);self.assertEqual([t["rule_id"] for t in json.loads(body)["trace"]],["R14","R20"])

    def test_invalid_json(self):
        self.assertEqual(self.request("/api/diagnose",b"{broken")[0],400)

    def test_invalid_choice(self):
        self.assertEqual(self.request("/api/diagnose",b'{"answers":{"soil":"flooded"}}')[0],400)

    def test_wrong_content_type(self):
        self.assertEqual(self.request("/api/diagnose",b"test","text/plain")[0],415)

    def test_private_files_not_exposed(self):
        self.assertEqual(self.request("/knowledge_base.py")[0],404)
        self.assertEqual(self.request("/../engine.py")[0],404)


if __name__ == "__main__":
    unittest.main(verbosity=2)
