import unittest
import warnings

from mt5linux.types import (
    MT5_TYPE_TAG,
    MT5_TYPES,
    OrderCheckResult,
    Tick,
    TradeRequest,
    materialize,
)


def _tagged(name, **fields):
    return {MT5_TYPE_TAG: name, **fields}


def _tick(**overrides):
    fields = {
        "time": 1585070338,
        "bid": 1.17264,
        "ask": 1.17279,
        "last": 0.0,
        "volume": 0,
        "time_msc": 1585070338728,
        "flags": 2,
        "volume_real": 0.0,
    }
    fields.update(overrides)
    return _tagged("Tick", **fields)


class MaterializeTests(unittest.TestCase):
    def test_tagged_dict_becomes_typed_record(self):
        record = materialize(_tick(time=1585070339, bid=1.5))

        self.assertIsInstance(record, Tick)
        self.assertEqual(record.time, 1585070339)
        self.assertEqual(record.bid, 1.5)

    def test_record_keeps_namedtuple_api(self):
        record = materialize(_tick())

        self.assertEqual(tuple(record._asdict()), Tick._fields)
        self.assertEqual(record._asdict()["bid"], 1.17264)
        self.assertEqual(
            tuple(record),
            (1585070338, 1.17264, 1.17279, 0.0, 0, 1585070338728, 2, 0.0),
        )

    def test_nested_records(self):
        plain = _tagged(
            "OrderCheckResult",
            retcode=0,
            balance=100.0,
            equity=100.0,
            profit=0.0,
            margin=0.0,
            margin_free=100.0,
            margin_level=0.0,
            comment="Done",
            request=_tagged(
                "TradeRequest",
                action=1,
                magic=0,
                order=0,
                symbol="EURUSD",
                volume=0.1,
                price=1.1,
                stoplimit=0.0,
                sl=0.0,
                tp=0.0,
                deviation=20,
                type=0,
                type_filling=2,
                type_time=0,
                expiration=0,
                comment="",
                position=0,
                position_by=0,
            ),
        )

        record = materialize(plain)

        self.assertIsInstance(record, OrderCheckResult)
        self.assertIsInstance(record.request, TradeRequest)
        self.assertEqual(record.request.symbol, "EURUSD")
        self.assertIsInstance(record._asdict()["request"], TradeRequest)

    def test_sequence_of_records(self):
        plain = [
            _tick(time=1, bid=1.0),
            _tick(time=2, bid=2.0),
        ]

        records = materialize(plain)

        self.assertIsInstance(records, list)
        self.assertTrue(all(isinstance(record, Tick) for record in records))
        self.assertEqual([record.time for record in records], [1, 2])

    def test_unknown_fields_are_dropped_with_warning(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            record = materialize(_tick(brand_new_field=3))

        self.assertEqual(len(caught), 1)
        self.assertIn("brand_new_field", str(caught[0].message))
        self.assertEqual(tuple(record._asdict()), Tick._fields)

    def test_untagged_structures_pass_through(self):
        plain = {"plain": [1, 2.0, "x"], "nested": {"a": 1}}

        self.assertEqual(materialize(plain), plain)
        self.assertEqual(materialize((1, 2)), (1, 2))
        self.assertEqual(materialize(None), None)

    def test_unknown_tag_passes_through_as_dict(self):
        plain = _tagged("FutureType", field=1)

        self.assertEqual(materialize(plain), {"field": 1})

    def test_registry_covers_all_defined_types(self):
        expected = {
            "AccountInfo",
            "BookInfo",
            "OrderCheckResult",
            "OrderSendResult",
            "SymbolInfo",
            "TerminalInfo",
            "Tick",
            "TradeDeal",
            "TradeOrder",
            "TradePosition",
            "TradeRequest",
        }

        self.assertEqual(set(MT5_TYPES), expected)
        self.assertTrue(all(cls._fields for cls in MT5_TYPES.values()))


if __name__ == "__main__":
    unittest.main()
