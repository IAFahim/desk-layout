import unittest

from desk_layout import (
    compile_deskflow_ini,
    compile_server_conf,
    compute_links,
    solve_layout_from_photo,
    to_forward_slash_path,
)


class DeskLayoutTests(unittest.TestCase):
    def setUp(self) -> None:
        self.nodes = {
            "P1": {"id": "P1", "computer_name": "main-pc", "tailscale_ip": "100.64.0.1", "display_w": 3840, "display_h": 1080},
            "P2": {"id": "P2", "computer_name": "workstation", "tailscale_ip": "100.64.0.2", "display_w": 1920, "display_h": 1080},
            "P3": {"id": "P3", "computer_name": "laptop", "tailscale_ip": "100.64.0.3", "display_w": 1920, "display_h": 1080},
            "P4": {"id": "P4", "computer_name": "mini-box", "tailscale_ip": "100.64.0.4", "display_w": 1920, "display_h": 1080},
        }

    def test_two_pc_side_by_side_and_ini_v127(self) -> None:
        layout = {
            "master_id": "P1",
            "items": [
                {"id": "P1", "x": 0.0, "y": 0.0, "w": 3.556, "h": 1.0},
                {"id": "P2", "x": 3.556, "y": 0.0, "w": 1.778, "h": 1.0},
            ],
        }
        srv = compile_server_conf(self.nodes, layout)
        self.assertNotIn("section: screens", srv)
        self.assertNotIn("section: aliases", srv)
        self.assertIn("section: links", srv)
        self.assertIn("section: options", srv)
        self.assertIn("right(0,100) = workstation(0,100)", srv)
        self.assertIn("left(0,100) = main-pc(0,100)", srv)

        ini = compile_deskflow_ini(
            "main-pc",
            "server",
            "100.64.0.1",
            "100.64.0.1",
            r"C:\Users\Test\AppData\Local\deskflow-fleet\deskflow-server.conf",
            computer_names=["main-pc", "workstation"],
        )
        self.assertIn("externalConfigFile=C:/Users/Test/AppData/Local/deskflow-fleet/deskflow-server.conf", ini)
        self.assertIn("tlsEnabled=false", ini)
        self.assertIn("interface=100.64.0.1", ini)
        self.assertIn("[computer_1]\nname=main-pc", ini)
        self.assertIn("[computer_2]\nname=workstation", ini)
        self.assertEqual(to_forward_slash_path(r"C:\a\b.conf"), "C:/a/b.conf")

    def test_l_shape_no_overlapping_intervals(self) -> None:
        # P1 on left (h=1.0), P2 top-right (h=0.5), P3 bottom-right (h=0.5)
        layout = {
            "master_id": "P1",
            "items": [
                {"id": "P1", "x": 0.0, "y": 0.0, "w": 1.778, "h": 1.0},
                {"id": "P2", "x": 1.778, "y": 0.0, "w": 1.778, "h": 0.5},
                {"id": "P3", "x": 1.778, "y": 0.5, "w": 1.778, "h": 0.5},
            ],
        }
        names = {"P1": "main-pc", "P2": "workstation", "P3": "laptop"}
        links = compute_links(layout["items"], names)
        p1_rights = [lk for lk in links["P1"] if lk["dir"] == "right"]
        self.assertEqual(len(p1_rights), 2)
        p1_rights.sort(key=lambda lk: lk["s0"])
        self.assertLessEqual(p1_rights[0]["s1"], p1_rights[1]["s0"])

    def test_solve_from_photo_row_and_grid(self) -> None:
        det2 = [
            {"code": "P1", "cx": 400, "cy": 500, "size": 120},
            {"code": "P2", "cx": 1100, "cy": 510, "size": 120},
        ]
        res2 = solve_layout_from_photo(det2, self.nodes)
        self.assertEqual(len(res2["items"]), 2)
        a, b = res2["items"]
        self.assertAlmostEqual(a["y"], b["y"], places=2)
        self.assertGreaterEqual(b["x"], a["x"] + a["w"] - 1e-3)

        det4 = [
            {"code": "P1", "cx": 420, "cy": 310, "size": 100},
            {"code": "P2", "cx": 1120, "cy": 315, "size": 100},
            {"code": "P3", "cx": 420, "cy": 800, "size": 100},
            {"code": "P4", "cx": 1120, "cy": 790, "size": 100},
        ]
        res4 = solve_layout_from_photo(det4, self.nodes)
        self.assertEqual(len(res4["items"]), 4)
        items = res4["items"]
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                x, y = items[i], items[j]
                ox = min(x["x"] + x["w"], y["x"] + y["w"]) - max(x["x"], y["x"])
                oy = min(x["y"] + x["h"], y["y"] + y["h"]) - max(x["y"], y["y"])
                self.assertFalse(ox > 1e-2 and oy > 1e-2, f"Overlap between {x['id']} and {y['id']}")


if __name__ == "__main__":
    unittest.main()
