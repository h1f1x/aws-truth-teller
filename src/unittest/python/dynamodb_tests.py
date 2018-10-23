import datetime
from dateutil.tz import tzlocal
import unittest2 as unittest

import aws_truth_teller.dynamodb as ddb


class DynamoDBTest(unittest.TestCase):
    ''' Testing some of the functions
    '''
    def test_compare_attributes(self):
        one = {'AttributeDefinitions': [{'AttributeName': 'Album', 'AttributeType': 'S'}, {'AttributeName': 'Artist', 'AttributeType': 'S'}], 'TableName': 'ddb-backup-restore-test-DynamoDBTable-1EM047Y3HR399', 'KeySchema': [{'AttributeName': 'Album', 'KeyType': 'HASH'}, {'AttributeName': 'Artist', 'KeyType': 'RANGE'}], 'TableStatus': 'ACTIVE', 'CreationDateTime': datetime.datetime(2018, 10, 22, 9, 1, 46, 817000, tzinfo=tzlocal()), 'ProvisionedThroughput': {'NumberOfDecreasesToday': 0, 'ReadCapacityUnits': 2, 'WriteCapacityUnits': 1}, 'TableSizeBytes': 0, 'ItemCount': 0, 'TableArn': 'arn:aws:dynamodb:eu-west-1:1234567890:table/ddb-backup-restore-test-DynamoDBTable-1EM047Y3HR399', 'TableId': 'b7dfafdb-59cb-4d90-b397-cc454ab0ddd0'}

        two = {'AttributeDefinitions': [{'AttributeName': 'Album', 'AttributeType': 'S'}, {'AttributeName': 'Artist', 'AttributeType': 'S'}], 'TableName': 'ddb-backup-restore-test-DynamoDBTable-1EM047Y3HR399', 'KeySchema': [{'AttributeName': 'Album', 'KeyType': 'HASH'}, {'AttributeName': 'Artist', 'KeyType': 'RANGE'}], 'TableStatus': 'ACTIVE', 'CreationDateTime': datetime.datetime(2018, 10, 22, 9, 6, 15, 479000, tzinfo=tzlocal()), 'ProvisionedThroughput': {'LastDecreaseDateTime': datetime.datetime(2018, 10, 22, 9, 12, 27, 942000, tzinfo=tzlocal()), 'NumberOfDecreasesToday': 1, 'ReadCapacityUnits': 2, 'WriteCapacityUnits': 1}, 'TableSizeBytes': 0, 'ItemCount': 0, 'TableArn': 'arn:aws:dynamodb:eu-west-1:1234567890:table/ddb-backup-restore-test-DynamoDBTable-1EM047Y3HR399', 'TableId': '3c87b495-5b83-4d96-8553-9e3c14f7af16'}

        self.assertEqual([], ddb.compare_attributes(one, one))
        self.assertTrue(1, len(ddb.compare_attributes(one, two)))

    def test_get_diff_attributes__empty(self):
        self.assertEqual(0, len(ddb.get_diff_attributes({}, {})))

    def test_get_diff_attributes__equals_itself(self):
        one = {'foo': 42, 'bar': 23}
        self.assertEqual(0, len(ddb.get_diff_attributes(one, one)))

    def test_get_diff_attributes__diff_against_empty(self):
        one = {'foo': 42}
        self.assertEqual(1, len(ddb.get_diff_attributes(one, {})))
        self.assertEqual(1, len(ddb.get_diff_attributes({}, one)))
        self.assertEqual({'foo': (42, 'key not found')}, ddb.get_diff_attributes(one, {}))

    def test_compare_attributes__equals_itself(self):
        one = {'foo': 42}
        self.assertEqual([], ddb.compare_attributes(one, one))

    def test_compare_attributes__with_diff_in_field_to_ignore(self):
        one = {'TableId': 0}
        self.assertEqual([], ddb.compare_attributes(one, one))
        self.assertEqual([], ddb.compare_attributes(one, {}))
