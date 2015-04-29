# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

import datetime
from django.conf import settings
from inventorum.ebay.lib.ebay.data import EbayParser
from inventorum.ebay.lib.ebay.notifications import EbayNotification


log = logging.getLogger(__name__)


def compile_notification_template(template, timestamp=None, signature=None, **kwargs):
    if timestamp is None:
        timestamp = datetime.datetime.utcnow()

    timestamp = timestamp.strftime(EbayParser.DATE_FORMAT)

    if signature is None:
        signature = EbayNotification.compute_signature(timestamp, settings.EBAY_DEVID,
                                                       settings.EBAY_APPID, settings.EBAY_CERTID)

    return template(timestamp, signature, **kwargs)


fixed_price_transaction_notification_template = lambda timestamp, signature: """<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
 <soapenv:Header>
  <ebl:RequesterCredentials soapenv:mustUnderstand="0" xmlns:ns="urn:ebay:apis:eBLBaseComponents" xmlns:ebl="urn:ebay:apis:eBLBaseComponents">
   <ebl:NotificationSignature xmlns:ebl="urn:ebay:apis:eBLBaseComponents">{signature}</ebl:NotificationSignature>
  </ebl:RequesterCredentials>
 </soapenv:Header>
 <soapenv:Body>
  <GetItemTransactionsResponse xmlns="urn:ebay:apis:eBLBaseComponents">
   <Timestamp>{timestamp}</Timestamp>
   <Ack>Success</Ack>
   <CorrelationID>586806200</CorrelationID>
   <Version>853</Version>
   <Build>E853_CORE_API_16609591_R1</Build>
   <NotificationEventName>FixedPriceTransaction</NotificationEventName>
   <RecipientUserID>testuser_michalhernas</RecipientUserID>
   <EIASToken>nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6wFk4GhCpiGpAqdj6x9nY+seQ==</EIASToken>
   <PaginationResult>
    <TotalNumberOfPages>1</TotalNumberOfPages>
    <TotalNumberOfEntries>1</TotalNumberOfEntries>
   </PaginationResult>
   <HasMoreTransactions>false</HasMoreTransactions>
   <TransactionsPerPage>100</TransactionsPerPage>
   <PageNumber>1</PageNumber>
   <ReturnedTransactionCountActual>1</ReturnedTransactionCountActual>
   <Item>
    <AutoPay>false</AutoPay>
    <BuyItNowPrice currencyID="EUR">0.0</BuyItNowPrice>
    <Currency>EUR</Currency>
    <ItemID>110136115192</ItemID>
    <ListingDetails>
     <StartTime>2014-01-16T15:19:06.000Z</StartTime>
     <EndTime>2014-01-26T15:19:06.000Z</EndTime>
     <ViewItemURL>http://cgi.sandbox.ebay.de/ws/eBayISAPI.dll?ViewItem&amp;Item=110136115192</ViewItemURL>
     <ExpressListing>false</ExpressListing>
     <ViewItemURLForNaturalSearch>http://cgi.sandbox.ebay.de/ws/eBayISAPI.dll?ViewItem&amp;item=110136115192&amp;category=0</ViewItemURLForNaturalSearch>
    </ListingDetails>
    <ListingType>FixedPriceItem</ListingType>
    <PaymentMethods>PayPal</PaymentMethods>
    <PrimaryCategory>
     <CategoryID>19526</CategoryID>
    </PrimaryCategory>
    <PrivateListing>false</PrivateListing>
    <Quantity>88</Quantity>
    <SecondaryCategory>
     <CategoryID>0</CategoryID>
    </SecondaryCategory>
    <Seller>
     <AboutMePage>false</AboutMePage>
     <EIASToken>nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6wFk4GhCpiGpAqdj6x9nY+seQ==</EIASToken>
     <Email>michal@hernas.pl</Email>
     <FeedbackScore>500</FeedbackScore>
     <PositiveFeedbackPercent>0.0</PositiveFeedbackPercent>
     <FeedbackPrivate>false</FeedbackPrivate>
     <FeedbackRatingStar>Purple</FeedbackRatingStar>
     <IDVerified>true</IDVerified>
     <eBayGoodStanding>true</eBayGoodStanding>
     <NewUser>false</NewUser>
     <RegistrationDate>1995-01-01T00:00:00.000Z</RegistrationDate>
     <Site>Germany</Site>
     <Status>Confirmed</Status>
     <UserID>testuser_michalhernas</UserID>
     <UserIDChanged>false</UserIDChanged>
     <UserIDLastChanged>2013-08-29T08:46:47.000Z</UserIDLastChanged>
     <VATStatus>VATTax</VATStatus>
     <SellerInfo>
      <AllowPaymentEdit>true</AllowPaymentEdit>
      <CheckoutEnabled>true</CheckoutEnabled>
      <CIPBankAccountStored>false</CIPBankAccountStored>
      <GoodStanding>true</GoodStanding>
      <LiveAuctionAuthorized>false</LiveAuctionAuthorized>
      <MerchandizingPref>OptIn</MerchandizingPref>
      <QualifiesForB2BVAT>false</QualifiesForB2BVAT>
      <SellerLevel>None</SellerLevel>
      <StoreOwner>false</StoreOwner>
      <ExpressEligible>false</ExpressEligible>
      <ExpressWallet>false</ExpressWallet>
      <SafePaymentExempt>true</SafePaymentExempt>
     </SellerInfo>
    </Seller>
    <SellingStatus>
     <ConvertedCurrentPrice currencyID="EUR">66.0</ConvertedCurrentPrice>
     <CurrentPrice currencyID="EUR">66.0</CurrentPrice>
     <QuantitySold>3</QuantitySold>
     <ListingStatus>Active</ListingStatus>
    </SellingStatus>
    <Site>Germany</Site>
    <StartPrice currencyID="EUR">66.0</StartPrice>
    <Title>Aba DUPLICATED</Title>
    <GetItFast>false</GetItFast>
    <IntegratedMerchantCreditCardEnabled>false</IntegratedMerchantCreditCardEnabled>
   </Item>
   <TransactionArray>
    <Transaction>
     <AmountPaid currencyID="EUR">136.9</AmountPaid>
     <AdjustmentAmount currencyID="EUR">0.0</AdjustmentAmount>
     <ConvertedAdjustmentAmount currencyID="EUR">0.0</ConvertedAdjustmentAmount>
     <Buyer>
      <AboutMePage>false</AboutMePage>
      <EIASToken>nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6wFk4GhCpiGow6dj6x9nY+seQ==</EIASToken>
      <Email>michal@inventorum.com</Email>
      <FeedbackScore>500</FeedbackScore>
      <PositiveFeedbackPercent>0.0</PositiveFeedbackPercent>
      <FeedbackPrivate>false</FeedbackPrivate>
      <FeedbackRatingStar>Purple</FeedbackRatingStar>
      <IDVerified>true</IDVerified>
      <eBayGoodStanding>true</eBayGoodStanding>
      <NewUser>false</NewUser>
      <RegistrationAddress>
       <Name>Test User</Name>
       <Street>address</Street>
       <Street1>address</Street1>
       <CityName>city</CityName>
       <StateOrProvince>Bad Oyenhausen</StateOrProvince>
       <Country>DE</Country>
       <CountryName>Deutschland</CountryName>
       <Phone>Invalid Request</Phone>
       <PostalCode>32547</PostalCode>
      </RegistrationAddress>
      <RegistrationDate>1995-01-01T00:00:00.000Z</RegistrationDate>
      <Site>Germany</Site>
      <Status>Confirmed</Status>
      <UserID>testuser_inventorum1234</UserID>
      <UserIDChanged>false</UserIDChanged>
      <UserIDLastChanged>2013-08-28T15:17:57.000Z</UserIDLastChanged>
      <VATStatus>VATTax</VATStatus>
      <BuyerInfo>
       <ShippingAddress>
        <Name>Test User</Name>
        <Street1>address</Street1>
        <CityName>city</CityName>
        <StateOrProvince>Bad Oyenhausen</StateOrProvince>
        <Country>DE</Country>
        <CountryName>Deutschland</CountryName>
        <Phone>Invalid Request</Phone>
        <PostalCode>32547</PostalCode>
        <AddressID>6977656</AddressID>
        <AddressOwner>eBay</AddressOwner>
       </ShippingAddress>
      </BuyerInfo>
      <UserAnonymized>false</UserAnonymized>
     </Buyer>
     <ShippingDetails>
      <ChangePaymentInstructions>true</ChangePaymentInstructions>
      <InsuranceFee currencyID="EUR">0.0</InsuranceFee>
      <InsuranceOption>NotOffered</InsuranceOption>
      <InsuranceWanted>false</InsuranceWanted>
      <PaymentEdited>false</PaymentEdited>
      <SalesTax>
       <SalesTaxPercent>0.0</SalesTaxPercent>
       <ShippingIncludedInTax>false</ShippingIncludedInTax>
       <SalesTaxAmount currencyID="EUR">0.0</SalesTaxAmount>
      </SalesTax>
      <ShippingServiceOptions>
       <ShippingService>DE_DHLPackchen</ShippingService>
       <ShippingServiceCost currencyID="EUR">0.0</ShippingServiceCost>
       <ShippingServiceAdditionalCost currencyID="EUR">0.0</ShippingServiceAdditionalCost>
       <ShippingServicePriority>1</ShippingServicePriority>
       <ExpeditedService>false</ExpeditedService>
       <ShippingTimeMin>1</ShippingTimeMin>
       <ShippingTimeMax>2</ShippingTimeMax>
      </ShippingServiceOptions>
      <ShippingType>Flat</ShippingType>
      <SellingManagerSalesRecordNumber>112</SellingManagerSalesRecordNumber>
      <ThirdPartyCheckout>false</ThirdPartyCheckout>
      <TaxTable/>
      <GetItFast>false</GetItFast>
     </ShippingDetails>
     <ConvertedAmountPaid currencyID="EUR">132.0</ConvertedAmountPaid>
     <ConvertedTransactionPrice currencyID="EUR">66.0</ConvertedTransactionPrice>
     <CreatedDate>2014-01-16T15:30:44.000Z</CreatedDate>
     <DepositType>None</DepositType>
     <QuantityPurchased>2</QuantityPurchased>
     <Status>
      <eBayPaymentStatus>NoPaymentFailure</eBayPaymentStatus>
      <CheckoutStatus>CheckoutIncomplete</CheckoutStatus>
      <LastTimeModified>2014-01-16T15:30:45.000Z</LastTimeModified>
      <PaymentMethodUsed>None</PaymentMethodUsed>
      <CompleteStatus>Incomplete</CompleteStatus>
      <BuyerSelectedShipping>false</BuyerSelectedShipping>
      <PaymentHoldStatus>None</PaymentHoldStatus>
      <IntegratedMerchantCreditCardEnabled>false</IntegratedMerchantCreditCardEnabled>
     </Status>
     <TransactionID>27209385001</TransactionID>
     <TransactionPrice currencyID="EUR">66.0</TransactionPrice>
     <BestOfferSale>false</BestOfferSale>
     <ShippingServiceSelected>
      <ShippingInsuranceCost currencyID="EUR">0.0</ShippingInsuranceCost>
      <ShippingService>DE_DHLPackchen</ShippingService>
      <ShippingServiceCost currencyID="EUR">4.90</ShippingServiceCost>
     </ShippingServiceSelected>
     <FinalValueFee currencyID="EUR">10.32</FinalValueFee>
     <TransactionPlatform>eBay</TransactionPlatform>
     <TransactionSiteID>Germany</TransactionSiteID>
     <Platform>eBay</Platform>
     <PayPalEmailAddress>ferry@inventorum.com</PayPalEmailAddress>
     <BuyerGuaranteePrice currencyID="EUR">20000.0</BuyerGuaranteePrice>
     <IntangibleItem>false</IntangibleItem>
    </Transaction>
   </TransactionArray>
  </GetItemTransactionsResponse>
 </soapenv:Body>
</soapenv:Envelope>""".format(timestamp=timestamp, signature=signature)


item_closed_notification_template = lambda timestamp, signature: """<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
 <soapenv:Header>
  <ebl:RequesterCredentials soapenv:mustUnderstand="0" xmlns:ns="urn:ebay:apis:eBLBaseComponents" xmlns:ebl="urn:ebay:apis:eBLBaseComponents">
   <ebl:NotificationSignature xmlns:ebl="urn:ebay:apis:eBLBaseComponents">{signature}</ebl:NotificationSignature>
  </ebl:RequesterCredentials>
 </soapenv:Header>
 <soapenv:Body>
  <GetItemResponse xmlns="urn:ebay:apis:eBLBaseComponents">
   <Timestamp>{timestamp}</Timestamp>
   <Ack>Success</Ack>
   <CorrelationID>277356516360</CorrelationID>
   <Version>857</Version>
   <Build>E857_INTL_API_16640004_R1</Build>
   <NotificationEventName>ItemClosed</NotificationEventName>
   <RecipientUserID>paydroid</RecipientUserID>
   <EIASToken>nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6AFkYKnDpiFoQ6dj6x9nY+seQ==</EIASToken>
   <Item>
    <AutoPay>false</AutoPay>
    <BuyerProtection>ItemIneligible</BuyerProtection>
    <BuyItNowPrice currencyID="EUR">0.0</BuyItNowPrice>
    <Country>DE</Country>
    <Currency>EUR</Currency>
    <Description>&lt;p style=&quot;margin: 0px; padding: 10px 0px 0px; border-width: 0px; font-style: normal; vertical-align: baseline; -webkit-text-size-adjust: none; font-variant: normal; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); line-height: 1.52em; font-weight: bold; font-size: 16px; font-family: Helvetica, Arial, sans-serif; color: rgb(44, 47, 47); &quot;&gt;&lt;h7 class=&quot;part2headline&quot; style=&quot;font-weight: normal; font-size: 22px; color: rgb(0, 0, 0); text-align: center; line-height: 1.5em; font-family: helvetica, arial, hirakakupro-w3, osaka, &apos;ms pgothic&apos;, sans-serif; &quot;&gt;Ein Stand für alle Fälle&lt;/h7&gt;&lt;span style=&quot;font-size: 13px; font-weight: normal; color: rgb(0, 0, 0); font-family: helvetica, arial, hirakakupro-w3, osaka, &apos;ms pgothic&apos;, sans-serif; line-height: 20px; text-align: -webkit-auto; &quot;&gt;&lt;/span&gt;&lt;p class=&quot;part2handmade&quot; style=&quot;font-weight: normal; margin: 0px; padding: 10px 0px 0px; font-size: 15px; color: rgb(130, 130, 130); width: 380px; line-height: 1.5em; font-family: helvetica, arial, hirakakupro-w3, osaka, &apos;ms pgothic&apos;, sans-serif; &quot;&gt;Der neue Paydroid Stand für das iPhone 5, iPad mini oder iPod touch 5G kombiniert Funktionalität mit hochwertigem Design. Hergestellt aus hochwertiger Keramik und von Hand poliert sieht es nicht nur im Wohnzimmer oder auf dem Nachttisch gut aus. Der Stand lässt sich auch einfach mitnehmen und im Büro, in der Bahn oder anderswo verwenden.&lt;/p&gt;&lt;/p&gt;&lt;p style=&quot;margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; padding-top: 0px; padding-right: 0px; padding-bottom: 15px; padding-left: 0px; border-top-width: 0px; border-right-width: 0px; border-bottom-width: 0px; border-left-width: 0px; border-style: initial; border-color: initial; font-weight: normal; font-style: normal; font-size: 13px; line-height: 1.52em; font-family: Helvetica, Arial, sans-serif; vertical-align: baseline; -webkit-text-size-adjust: none; color: rgb(44, 47, 47); font-variant: normal; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); &quot;&gt;&lt;br&gt;&lt;h7 class=&quot;part2headline&quot; style=&quot;font-size: 22px; color: rgb(0, 0, 0); text-align: center; line-height: 1.5em; font-family: helvetica, arial, hirakakupro-w3, osaka, &apos;ms pgothic&apos;, sans-serif; &quot;&gt;Handmade in Germany - Innen wie Außen&lt;/h7&gt;&lt;span style=&quot;color: rgb(0, 0, 0); font-family: helvetica, arial, hirakakupro-w3, osaka, &apos;ms pgothic&apos;, sans-serif; line-height: 20px; text-align: -webkit-auto; &quot;&gt;&lt;/span&gt;&lt;p class=&quot;part2handmade&quot; style=&quot;margin: 0px; padding: 10px 0px 0px; font-size: 15px; color: rgb(130, 130, 130); width: 380px; line-height: 1.5em; font-family: helvetica, arial, hirakakupro-w3, osaka, &apos;ms pgothic&apos;, sans-serif; &quot;&gt;Wie unser iPad Dock wird auch der neue Paydroid Stand aus einem einzigen Block gefertigt. So ist der Stand stabil, robust und formschön. Durch diese Bauweise entsteht eine hochwertige und klare Designlinie mit wenig Komponenten. Jeder Paydroid Stand wird von Hand gefertigt und veredelt.&lt;/p&gt;&lt;/p&gt;&lt;p style=&quot;margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; padding-top: 0px; padding-right: 0px; padding-bottom: 15px; padding-left: 0px; border-top-width: 0px; border-right-width: 0px; border-bottom-width: 0px; border-left-width: 0px; border-style: initial; border-color: initial; font-weight: normal; font-style: normal; font-size: 13px; line-height: 1.52em; font-family: Helvetica, Arial, sans-serif; vertical-align: baseline; -webkit-text-size-adjust: none; color: rgb(44, 47, 47); font-variant: normal; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); &quot;&gt;&lt;br&gt;&lt;/p&gt;&lt;p style=&quot;margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; padding-top: 0px; padding-right: 0px; padding-bottom: 15px; padding-left: 0px; border-top-width: 0px; border-right-width: 0px; border-bottom-width: 0px; border-left-width: 0px; border-style: initial; border-color: initial; font-style: normal; font-size: 13px; line-height: 1.52em; font-family: Helvetica, Arial, sans-serif; vertical-align: baseline; -webkit-text-size-adjust: none; color: rgb(44, 47, 47); font-variant: normal; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); &quot;&gt;&lt;b&gt;Hinweis: Apple iPad mini nicht im Lieferumfang enthalten.&lt;/b&gt;&lt;/p&gt;</Description>
    <GiftIcon>0</GiftIcon>
    <HitCounter>NoHitCounter</HitCounter>
    <ItemID>110136115192</ItemID>
    <ListingDetails>
     <Adult>false</Adult>
     <BindingAuction>false</BindingAuction>
     <CheckoutEnabled>true</CheckoutEnabled>
     <ConvertedBuyItNowPrice currencyID="EUR">0.0</ConvertedBuyItNowPrice>
     <ConvertedStartPrice currencyID="EUR">19.0</ConvertedStartPrice>
     <ConvertedReservePrice currencyID="EUR">0.0</ConvertedReservePrice>
     <HasReservePrice>false</HasReservePrice>
     <StartTime>2014-02-10T14:54:57.000Z</StartTime>
     <EndTime>2014-02-10T15:03:32.000Z</EndTime>
     <ViewItemURL>http://www.ebay.de/itm/Paydroid-Stand-iPhone-iPad-mini-iPod-touch-/281263854028</ViewItemURL>
     <HasUnansweredQuestions>false</HasUnansweredQuestions>
     <HasPublicMessages>false</HasPublicMessages>
     <ViewItemURLForNaturalSearch>http://www.ebay.de/itm/Paydroid-Stand-iPhone-iPad-mini-iPod-touch-/281263854028</ViewItemURLForNaturalSearch>
     <EndingReason>OtherListingError</EndingReason>
    </ListingDetails>
    <ListingDesigner>
     <LayoutID>7710000</LayoutID>
     <ThemeID>7710</ThemeID>
    </ListingDesigner>
    <ListingDuration>Days_10</ListingDuration>
    <ListingType>FixedPriceItem</ListingType>
    <Location>Bad Honnef</Location>
    <PaymentMethods>CashOnPickup</PaymentMethods>
    <PrimaryCategory>
     <CategoryID>35190</CategoryID>
     <CategoryName>Handys &amp; Kommunikation:Handy- &amp; PDA-Zubehör:Halterungen</CategoryName>
    </PrimaryCategory>
    <PrivateListing>false</PrivateListing>
    <Quantity>5</Quantity>
    <ReservePrice currencyID="EUR">0.0</ReservePrice>
    <ReviseStatus>
     <ItemRevised>true</ItemRevised>
    </ReviseStatus>
    <Seller>
     <AboutMePage>false</AboutMePage>
     <Email>info@paydroid.de</Email>
     <FeedbackScore>1</FeedbackScore>
     <PositiveFeedbackPercent>0.0</PositiveFeedbackPercent>
     <FeedbackPrivate>false</FeedbackPrivate>
     <FeedbackRatingStar>None</FeedbackRatingStar>
     <IDVerified>false</IDVerified>
     <eBayGoodStanding>true</eBayGoodStanding>
     <NewUser>false</NewUser>
     <RegistrationDate>2012-04-25T12:14:28.000Z</RegistrationDate>
     <Site>Germany</Site>
     <Status>Confirmed</Status>
     <UserID>paydroid</UserID>
     <UserIDChanged>false</UserIDChanged>
     <UserIDLastChanged>2012-04-25T12:13:56.000Z</UserIDLastChanged>
     <VATStatus>VATTax</VATStatus>
     <SellerInfo>
      <AllowPaymentEdit>false</AllowPaymentEdit>
      <CheckoutEnabled>true</CheckoutEnabled>
      <CIPBankAccountStored>true</CIPBankAccountStored>
      <GoodStanding>true</GoodStanding>
      <LiveAuctionAuthorized>false</LiveAuctionAuthorized>
      <MerchandizingPref>OptIn</MerchandizingPref>
      <QualifiesForB2BVAT>false</QualifiesForB2BVAT>
      <StoreOwner>false</StoreOwner>
      <SellerBusinessType>Commercial</SellerBusinessType>
      <SafePaymentExempt>false</SafePaymentExempt>
     </SellerInfo>
     <MotorsDealer>false</MotorsDealer>
    </Seller>
    <SellingStatus>
     <BidCount>0</BidCount>
     <BidIncrement currencyID="EUR">0.0</BidIncrement>
     <ConvertedCurrentPrice currencyID="EUR">19.0</ConvertedCurrentPrice>
     <CurrentPrice currencyID="EUR">19.0</CurrentPrice>
     <LeadCount>0</LeadCount>
     <MinimumToBid currencyID="EUR">19.0</MinimumToBid>
     <QuantitySold>0</QuantitySold>
     <ReserveMet>true</ReserveMet>
     <SecondChanceEligible>false</SecondChanceEligible>
     <ListingStatus>Completed</ListingStatus>
     <QuantitySoldByPickupInStore>0</QuantitySoldByPickupInStore>
    </SellingStatus>
    <ShippingDetails>
     <ApplyShippingDiscount>false</ApplyShippingDiscount>
     <CalculatedShippingRate>
      <WeightMajor measurementSystem="Metric" unit="kg">0</WeightMajor>
      <WeightMinor measurementSystem="Metric" unit="gm">0</WeightMinor>
     </CalculatedShippingRate>
     <InsuranceFee currencyID="EUR">0.0</InsuranceFee>
     <InsuranceOption>NotOffered</InsuranceOption>
     <SalesTax>
      <SalesTaxPercent>0.0</SalesTaxPercent>
      <ShippingIncludedInTax>false</ShippingIncludedInTax>
     </SalesTax>
     <ShippingServiceOptions>
      <ShippingService>DE_DeutschePostBrief</ShippingService>
      <ShippingServiceCost currencyID="EUR">0.0</ShippingServiceCost>
      <ShippingServiceAdditionalCost currencyID="EUR">0.0</ShippingServiceAdditionalCost>
      <ShippingServicePriority>1</ShippingServicePriority>
      <ExpeditedService>false</ExpeditedService>
      <ShippingTimeMin>1</ShippingTimeMin>
      <ShippingTimeMax>2</ShippingTimeMax>
      <FreeShipping>true</FreeShipping>
     </ShippingServiceOptions>
     <ShippingType>Flat</ShippingType>
     <ThirdPartyCheckout>false</ThirdPartyCheckout>
     <InsuranceDetails>
      <InsuranceOption>NotOffered</InsuranceOption>
     </InsuranceDetails>
     <ShippingDiscountProfileID>0</ShippingDiscountProfileID>
     <InternationalShippingDiscountProfileID>0</InternationalShippingDiscountProfileID>
     <ExcludeShipToLocation>Africa</ExcludeShipToLocation>
     <ExcludeShipToLocation>Asia</ExcludeShipToLocation>
     <ExcludeShipToLocation>Central America and Caribbean</ExcludeShipToLocation>
     <ExcludeShipToLocation>Europe</ExcludeShipToLocation>
     <ExcludeShipToLocation>Middle East</ExcludeShipToLocation>
     <ExcludeShipToLocation>North America</ExcludeShipToLocation>
     <ExcludeShipToLocation>Oceania</ExcludeShipToLocation>
     <ExcludeShipToLocation>Southeast Asia</ExcludeShipToLocation>
     <ExcludeShipToLocation>South America</ExcludeShipToLocation>
     <ExcludeShipToLocation>PO Box</ExcludeShipToLocation>
     <ExcludeShipToLocation>Packstation</ExcludeShipToLocation>
     <SellerExcludeShipToLocationsPreference>false</SellerExcludeShipToLocationsPreference>
    </ShippingDetails>
    <ShipToLocations>DE</ShipToLocations>
    <Site>Germany</Site>
    <StartPrice currencyID="EUR">19.0</StartPrice>
    <TimeLeft>PT0S</TimeLeft>
    <Title>Paydroid Stand für iPhone + iPad mini + iPod touch</Title>
    <VATDetails>
     <VATPercent>19.0</VATPercent>
    </VATDetails>
    <HitCount>4</HitCount>
    <LocationDefaulted>true</LocationDefaulted>
    <GetItFast>false</GetItFast>
    <PostalCode>53604</PostalCode>
    <PictureDetails>
     <GalleryType>Gallery</GalleryType>
     <GalleryURL>http://i.ebayimg.com/00/s/NzQ4WDEwMjQ=/z/x90AAMXQBg5Rvrfr/$(KGrHqVHJFIFG-mN(q46BRvrfrMbOw~~60_1.JPG?set_id=8800005007</GalleryURL>
     <PhotoDisplay>None</PhotoDisplay>
     <PictureURL>http://i.ebayimg.com/00/s/NzQ4WDEwMjQ=/z/ZhsAAOxyKsZRvrft/$T2eC16dHJHIFFhJTCS+3BRvrftkgS!~~60_1.JPG?set_id=8800005007</PictureURL>
     <PictureURL>http://i.ebayimg.com/00/s/NzQ4WDEwMjQ=/z/QkwAAOxyLchRvrfp/$T2eC16FHJGoFFvohSJ5!BRvrfojwng~~60_1.JPG?set_id=8800005007</PictureURL>
     <PictureURL>http://i.ebayimg.com/00/s/NzQ4WDEwMjQ=/z/x90AAMXQBg5Rvrfr/$(KGrHqVHJFIFG-mN(q46BRvrfrMbOw~~60_1.JPG?set_id=8800005007</PictureURL>
     <PictureURL>http://i.ebayimg.com/00/s/NzQ4WDEwMjQ=/z/8PMAAMXQlgtRvru~/$T2eC16dHJFoE9nh6piThBRvru-6QkQ~~60_1.JPG?set_id=8800005007</PictureURL>
     <PictureURL>http://i.ebayimg.com/00/s/NzQ4WDEwMjQ=/z/0qwAAOxy--NRvrfw/$T2eC16JHJIQE9qUHrVqFBRvrfvzlvw~~60_1.JPG?set_id=8800005007</PictureURL>
     <PictureSource>EPS</PictureSource>
     <GalleryStatus>ImageProcessingError</GalleryStatus>
     <GalleryErrorInfo>Es ist uns nicht möglich, das genaue Problem bei http://i.ebayimg.com/00/s/NzQ4WDEwMjQ=/z/x90AAMXQBg5Rvrfr/$(KGrHqVHJFIFG-mN(q46BRvrfrMbOw~~60_1.JPG?set_id=8800005007 festzustellen. Wenn Sie sich informieren möchten, wie Sie dieses Problem lösen können, gehen Sie bitte zur folgenden eBay-Online-Hilfeseite: http://pages.ebay.de/help/sell/fix_gallery.html</GalleryErrorInfo>
    </PictureDetails>
    <DispatchTimeMax>1</DispatchTimeMax>
    <ProxyItem>false</ProxyItem>
    <BusinessSellerDetails>
     <Address>
      <Street1>Königin-Sophie-Str. 4</Street1>
      <CityName>Bad Honnef</CityName>
      <StateOrProvince>default</StateOrProvince>
      <CountryName>Deutschland</CountryName>
      <Phone>022249886389</Phone>
      <PostalCode>53604</PostalCode>
      <CompanyName>Paydroid UG (haftungsbeschränkt)</CompanyName>
      <FirstName>Ferry</FirstName>
      <LastName>Hötzel</LastName>
     </Address>
     <Fax>022249886379</Fax>
     <Email>info@paydroid.de</Email>
     <TradeRegistrationNumber>HRB 11303</TradeRegistrationNumber>
     <LegalInvoice>true</LegalInvoice>
     <TermsAndConditions>123</TermsAndConditions>
     <VATDetails>
      <VATSite>DE</VATSite>
      <VATID> DE275058598</VATID>
     </VATDetails>
    </BusinessSellerDetails>
    <BuyerGuaranteePrice currencyID="EUR">20000.0</BuyerGuaranteePrice>
    <BuyerRequirementDetails>
     <ShipToRegistrationCountry>true</ShipToRegistrationCountry>
    </BuyerRequirementDetails>
    <ReturnPolicy>
     <ReturnsWithinOption>Days_14</ReturnsWithinOption>
     <ReturnsWithin>14 Tage</ReturnsWithin>
     <ReturnsAcceptedOption>ReturnsAccepted</ReturnsAcceptedOption>
     <ReturnsAccepted>Verbraucher haben das Recht, den Artikel unter den angegebenen Bedingungen zurückzugeben.</ReturnsAccepted>
     <Description></Description>
     <ShippingCostPaidByOption>EUBuyer_CancelRightsUnder40</ShippingCostPaidByOption>
     <ShippingCostPaidBy>Widerrufsrecht: Käufer trägt die regelmäßigen Kosten der Rücksendung, wenn die gelieferte Ware der bestellten entspricht und der Preis der zurückzusendenden Sache 40 Euro nicht übersteigt oder wenn der Käufer bei einem höheren Preis zum Zeitpunkt des Widerrufs noch nicht den Kaufpreis bezahlt oder eine vertraglich vereinbarte Teilzahlung erbracht hat.</ShippingCostPaidBy>
    </ReturnPolicy>
    <ConditionID>1000</ConditionID>
    <ConditionDisplayName>Neu</ConditionDisplayName>
    <PostCheckoutExperienceEnabled>false</PostCheckoutExperienceEnabled>
    <SellerProfiles>
     <SellerShippingProfile>
      <ShippingProfileID>37501926018</ShippingProfileID>
      <ShippingProfileName>Versandbedingungen 99422718</ShippingProfileName>
     </SellerShippingProfile>
     <SellerReturnProfile>
      <ReturnProfileID>49370735018</ReturnProfileID>
      <ReturnProfileName>Rücknahmebedingungen 65666597</ReturnProfileName>
     </SellerReturnProfile>
     <SellerPaymentProfile>
      <PaymentProfileID>49370738018</PaymentProfileID>
      <PaymentProfileName>Zahlungsbedingungen 44853318</PaymentProfileName>
     </SellerPaymentProfile>
    </SellerProfiles>
    <ShippingPackageDetails>
     <ShippingIrregular>false</ShippingIrregular>
     <ShippingPackage>PackageThickEnvelope</ShippingPackage>
     <WeightMajor measurementSystem="Metric" unit="kg">0</WeightMajor>
     <WeightMinor measurementSystem="Metric" unit="gm">0</WeightMinor>
    </ShippingPackageDetails>
    <HideFromSearch>false</HideFromSearch>
   </Item>
  </GetItemResponse>
 </soapenv:Body>
</soapenv:Envelope>""".format(timestamp=timestamp, signature=signature)


item_sold_notification_template = lambda timestamp, signature: """<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
 <soapenv:Header>
  <ebl:RequesterCredentials soapenv:mustUnderstand="0" xmlns:ns="urn:ebay:apis:eBLBaseComponents" xmlns:ebl="urn:ebay:apis:eBLBaseComponents">
   <ebl:NotificationSignature xmlns:ebl="urn:ebay:apis:eBLBaseComponents">{signature}</ebl:NotificationSignature>
  </ebl:RequesterCredentials>
 </soapenv:Header>
 <soapenv:Body>
  <GetItemResponse xmlns="urn:ebay:apis:eBLBaseComponents">
   <Timestamp>{timestamp}</Timestamp>
   <Ack>Success</Ack>
   <CorrelationID>275708863631</CorrelationID>
   <Version>857</Version>
   <Build>E857_INTL_API_16640004_R1</Build>
   <NotificationEventName>ItemSold</NotificationEventName>
   <RecipientUserID>paydroid</RecipientUserID>
   <EIASToken>nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6AFkYKnDpiFoQ6dj6x9nY+seQ==</EIASToken>
   <Item>
    <AutoPay>false</AutoPay>
    <BuyerProtection>ItemEligible</BuyerProtection>
    <BuyItNowPrice currencyID="EUR">0.0</BuyItNowPrice>
    <Country>DE</Country>
    <Currency>EUR</Currency>
    <Description>&lt;p style=&quot;margin: 0px; padding: 10px 0px 0px; border-width: 0px; font-style: normal; vertical-align: baseline; -webkit-text-size-adjust: none; font-variant: normal; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); line-height: 1.52em; font-weight: bold; font-size: 16px; font-family: Helvetica, Arial, sans-serif; color: rgb(44, 47, 47); &quot;&gt;&lt;h7 class=&quot;part2headline&quot; style=&quot;font-weight: normal; font-size: 22px; color: rgb(0, 0, 0); text-align: center; line-height: 1.5em; font-family: helvetica, arial, hirakakupro-w3, osaka, &apos;ms pgothic&apos;, sans-serif; &quot;&gt;Ein Stand für alle Fälle&lt;/h7&gt;&lt;span style=&quot;font-size: 13px; font-weight: normal; color: rgb(0, 0, 0); font-family: helvetica, arial, hirakakupro-w3, osaka, &apos;ms pgothic&apos;, sans-serif; line-height: 20px; text-align: -webkit-auto; &quot;&gt;&lt;/span&gt;&lt;p class=&quot;part2handmade&quot; style=&quot;font-weight: normal; margin: 0px; padding: 10px 0px 0px; font-size: 15px; color: rgb(130, 130, 130); width: 380px; line-height: 1.5em; font-family: helvetica, arial, hirakakupro-w3, osaka, &apos;ms pgothic&apos;, sans-serif; &quot;&gt;Der neue Paydroid Stand für das iPhone 5, iPad mini oder iPod touch 5G kombiniert Funktionalität mit hochwertigem Design. Hergestellt aus hochwertiger Keramik und von Hand poliert sieht es nicht nur im Wohnzimmer oder auf dem Nachttisch gut aus. Der Stand lässt sich auch einfach mitnehmen und im Büro, in der Bahn oder anderswo verwenden.&lt;/p&gt;&lt;/p&gt;&lt;p style=&quot;margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; padding-top: 0px; padding-right: 0px; padding-bottom: 15px; padding-left: 0px; border-top-width: 0px; border-right-width: 0px; border-bottom-width: 0px; border-left-width: 0px; border-style: initial; border-color: initial; font-weight: normal; font-style: normal; font-size: 13px; line-height: 1.52em; font-family: Helvetica, Arial, sans-serif; vertical-align: baseline; -webkit-text-size-adjust: none; color: rgb(44, 47, 47); font-variant: normal; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); &quot;&gt;&lt;br&gt;&lt;h7 class=&quot;part2headline&quot; style=&quot;font-size: 22px; color: rgb(0, 0, 0); text-align: center; line-height: 1.5em; font-family: helvetica, arial, hirakakupro-w3, osaka, &apos;ms pgothic&apos;, sans-serif; &quot;&gt;Handmade in Germany - Innen wie Außen&lt;/h7&gt;&lt;span style=&quot;color: rgb(0, 0, 0); font-family: helvetica, arial, hirakakupro-w3, osaka, &apos;ms pgothic&apos;, sans-serif; line-height: 20px; text-align: -webkit-auto; &quot;&gt;&lt;/span&gt;&lt;p class=&quot;part2handmade&quot; style=&quot;margin: 0px; padding: 10px 0px 0px; font-size: 15px; color: rgb(130, 130, 130); width: 380px; line-height: 1.5em; font-family: helvetica, arial, hirakakupro-w3, osaka, &apos;ms pgothic&apos;, sans-serif; &quot;&gt;Wie unser iPad Dock wird auch der neue Paydroid Stand aus einem einzigen Block gefertigt. So ist der Stand stabil, robust und formschön. Durch diese Bauweise entsteht eine hochwertige und klare Designlinie mit wenig Komponenten. Jeder Paydroid Stand wird von Hand gefertigt und veredelt.&lt;/p&gt;&lt;/p&gt;&lt;p style=&quot;margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; padding-top: 0px; padding-right: 0px; padding-bottom: 15px; padding-left: 0px; border-top-width: 0px; border-right-width: 0px; border-bottom-width: 0px; border-left-width: 0px; border-style: initial; border-color: initial; font-weight: normal; font-style: normal; font-size: 13px; line-height: 1.52em; font-family: Helvetica, Arial, sans-serif; vertical-align: baseline; -webkit-text-size-adjust: none; color: rgb(44, 47, 47); font-variant: normal; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); &quot;&gt;&lt;br&gt;&lt;/p&gt;&lt;p style=&quot;margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; padding-top: 0px; padding-right: 0px; padding-bottom: 15px; padding-left: 0px; border-top-width: 0px; border-right-width: 0px; border-bottom-width: 0px; border-left-width: 0px; border-style: initial; border-color: initial; font-style: normal; font-size: 13px; line-height: 1.52em; font-family: Helvetica, Arial, sans-serif; vertical-align: baseline; -webkit-text-size-adjust: none; color: rgb(44, 47, 47); font-variant: normal; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; background-color: rgb(255, 255, 255); &quot;&gt;&lt;b&gt;Hinweis: Apple iPad mini nicht im Lieferumfang enthalten.&lt;/b&gt;&lt;/p&gt;</Description>
    <GiftIcon>0</GiftIcon>
    <HitCounter>NoHitCounter</HitCounter>
    <ItemID>110136115192</ItemID>
    <ListingDetails>
     <Adult>false</Adult>
     <BindingAuction>false</BindingAuction>
     <CheckoutEnabled>true</CheckoutEnabled>
     <ConvertedBuyItNowPrice currencyID="EUR">0.0</ConvertedBuyItNowPrice>
     <ConvertedStartPrice currencyID="EUR">19.0</ConvertedStartPrice>
     <ConvertedReservePrice currencyID="EUR">0.0</ConvertedReservePrice>
     <HasReservePrice>false</HasReservePrice>
     <StartTime>2014-02-04T11:30:41.000Z</StartTime>
     <EndTime>2014-02-09T10:26:58.000Z</EndTime>
     <ViewItemURL>http://www.ebay.de/itm/Paydroid-Stand-iPhone-iPad-mini-iPod-touch-/281259738295</ViewItemURL>
     <HasUnansweredQuestions>false</HasUnansweredQuestions>
     <HasPublicMessages>false</HasPublicMessages>
     <ViewItemURLForNaturalSearch>http://www.ebay.de/itm/Paydroid-Stand-iPhone-iPad-mini-iPod-touch-/281259738295</ViewItemURLForNaturalSearch>
    </ListingDetails>
    <ListingDesigner>
     <LayoutID>7710000</LayoutID>
     <ThemeID>7710</ThemeID>
    </ListingDesigner>
    <ListingDuration>Days_5</ListingDuration>
    <ListingType>FixedPriceItem</ListingType>
    <Location>Bad Honnef</Location>
    <PaymentMethods>PayPal</PaymentMethods>
    <PayPalEmailAddress>info@paydroid.de</PayPalEmailAddress>
    <PrimaryCategory>
     <CategoryID>35190</CategoryID>
     <CategoryName>Handys &amp; Kommunikation:Handy- &amp; PDA-Zubehör:Halterungen</CategoryName>
    </PrimaryCategory>
    <PrivateListing>false</PrivateListing>
    <Quantity>1</Quantity>
    <ReservePrice currencyID="EUR">0.0</ReservePrice>
    <ReviseStatus>
     <ItemRevised>true</ItemRevised>
    </ReviseStatus>
    <Seller>
     <AboutMePage>false</AboutMePage>
     <Email>info@paydroid.de</Email>
     <FeedbackScore>1</FeedbackScore>
     <PositiveFeedbackPercent>0.0</PositiveFeedbackPercent>
     <FeedbackPrivate>false</FeedbackPrivate>
     <FeedbackRatingStar>None</FeedbackRatingStar>
     <IDVerified>false</IDVerified>
     <eBayGoodStanding>true</eBayGoodStanding>
     <NewUser>false</NewUser>
     <RegistrationDate>2012-04-25T12:14:28.000Z</RegistrationDate>
     <Site>Germany</Site>
     <Status>Confirmed</Status>
     <UserID>paydroid</UserID>
     <UserIDChanged>false</UserIDChanged>
     <UserIDLastChanged>2012-04-25T12:13:56.000Z</UserIDLastChanged>
     <VATStatus>VATTax</VATStatus>
     <SellerInfo>
      <AllowPaymentEdit>false</AllowPaymentEdit>
      <CheckoutEnabled>true</CheckoutEnabled>
      <CIPBankAccountStored>true</CIPBankAccountStored>
      <GoodStanding>true</GoodStanding>
      <LiveAuctionAuthorized>false</LiveAuctionAuthorized>
      <MerchandizingPref>OptIn</MerchandizingPref>
      <QualifiesForB2BVAT>false</QualifiesForB2BVAT>
      <StoreOwner>false</StoreOwner>
      <SellerBusinessType>Commercial</SellerBusinessType>
      <SafePaymentExempt>false</SafePaymentExempt>
     </SellerInfo>
     <MotorsDealer>false</MotorsDealer>
    </Seller>
    <SellingStatus>
     <BidCount>0</BidCount>
     <BidIncrement currencyID="EUR">0.0</BidIncrement>
     <ConvertedCurrentPrice currencyID="EUR">19.0</ConvertedCurrentPrice>
     <CurrentPrice currencyID="EUR">19.0</CurrentPrice>
     <HighBidder>
      <AboutMePage>false</AboutMePage>
      <EIASToken>nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6wGkoKoCJmKqQ6dj6x9nY+seQ==</EIASToken>
      <Email>richardgreiss@icloud.com</Email>
      <FeedbackScore>260</FeedbackScore>
      <PositiveFeedbackPercent>100.0</PositiveFeedbackPercent>
      <FeedbackPrivate>false</FeedbackPrivate>
      <FeedbackRatingStar>Turquoise</FeedbackRatingStar>
      <IDVerified>false</IDVerified>
      <eBayGoodStanding>true</eBayGoodStanding>
      <NewUser>false</NewUser>
      <RegistrationAddress>
       <Name>Richard Greiss</Name>
       <Street>Lichtenbergplatz 4</Street>
       <Street1>Lichtenbergplatz 4</Street1>
       <CityName>Hannover</CityName>
       <Country>DE</Country>
       <CountryName>Deutschland</CountryName>
       <Phone>Invalid Request</Phone>
       <PostalCode>30449</PostalCode>
      </RegistrationAddress>
      <RegistrationDate>2005-08-09T07:18:43.000Z</RegistrationDate>
      <Site>Germany</Site>
      <Status>Confirmed</Status>
      <UserID>blackholecandidate</UserID>
      <UserIDChanged>false</UserIDChanged>
      <UserIDLastChanged>2005-08-09T07:15:41.000Z</UserIDLastChanged>
      <VATStatus>VATTax</VATStatus>
      <UserAnonymized>false</UserAnonymized>
     </HighBidder>
     <LeadCount>0</LeadCount>
     <MinimumToBid currencyID="EUR">19.0</MinimumToBid>
     <QuantitySold>1</QuantitySold>
     <ReserveMet>true</ReserveMet>
     <SecondChanceEligible>false</SecondChanceEligible>
     <ListingStatus>Completed</ListingStatus>
     <QuantitySoldByPickupInStore>0</QuantitySoldByPickupInStore>
    </SellingStatus>
    <ShippingDetails>
     <ApplyShippingDiscount>false</ApplyShippingDiscount>
     <CalculatedShippingRate>
      <WeightMajor measurementSystem="Metric" unit="kg">0</WeightMajor>
      <WeightMinor measurementSystem="Metric" unit="gm">0</WeightMinor>
     </CalculatedShippingRate>
     <InsuranceFee currencyID="EUR">0.0</InsuranceFee>
     <InsuranceOption>NotOffered</InsuranceOption>
     <SalesTax>
      <SalesTaxPercent>0.0</SalesTaxPercent>
      <ShippingIncludedInTax>false</ShippingIncludedInTax>
     </SalesTax>
     <ShippingServiceOptions>
      <ShippingService>DE_DeutschePostBrief</ShippingService>
      <ShippingServiceCost currencyID="EUR">0.0</ShippingServiceCost>
      <ShippingServicePriority>1</ShippingServicePriority>
      <ExpeditedService>false</ExpeditedService>
      <ShippingTimeMin>1</ShippingTimeMin>
      <ShippingTimeMax>2</ShippingTimeMax>
      <FreeShipping>true</FreeShipping>
     </ShippingServiceOptions>
     <ShippingType>Flat</ShippingType>
     <ThirdPartyCheckout>false</ThirdPartyCheckout>
     <InsuranceDetails>
      <InsuranceOption>NotOffered</InsuranceOption>
     </InsuranceDetails>
     <ShippingDiscountProfileID>0</ShippingDiscountProfileID>
     <InternationalShippingDiscountProfileID>0</InternationalShippingDiscountProfileID>
     <ExcludeShipToLocation>Africa</ExcludeShipToLocation>
     <ExcludeShipToLocation>Asia</ExcludeShipToLocation>
     <ExcludeShipToLocation>Central America and Caribbean</ExcludeShipToLocation>
     <ExcludeShipToLocation>Europe</ExcludeShipToLocation>
     <ExcludeShipToLocation>Middle East</ExcludeShipToLocation>
     <ExcludeShipToLocation>North America</ExcludeShipToLocation>
     <ExcludeShipToLocation>Oceania</ExcludeShipToLocation>
     <ExcludeShipToLocation>Southeast Asia</ExcludeShipToLocation>
     <ExcludeShipToLocation>South America</ExcludeShipToLocation>
     <ExcludeShipToLocation>PO Box</ExcludeShipToLocation>
     <ExcludeShipToLocation>Packstation</ExcludeShipToLocation>
     <SellerExcludeShipToLocationsPreference>false</SellerExcludeShipToLocationsPreference>
    </ShippingDetails>
    <ShipToLocations>DE</ShipToLocations>
    <Site>Germany</Site>
    <StartPrice currencyID="EUR">19.0</StartPrice>
    <TimeLeft>PT0S</TimeLeft>
    <Title>Paydroid Stand für iPhone + iPad mini + iPod touch</Title>
    <VATDetails>
     <VATPercent>19.0</VATPercent>
    </VATDetails>
    <HitCount>9</HitCount>
    <LocationDefaulted>true</LocationDefaulted>
    <GetItFast>false</GetItFast>
    <PostalCode>53604</PostalCode>
    <PictureDetails>
     <GalleryType>Gallery</GalleryType>
     <GalleryURL>http://i.ebayimg.com/00/s/NzQ4WDEwMjQ=/z/x90AAMXQBg5Rvrfr/$(KGrHqVHJFIFG-mN(q46BRvrfrMbOw~~60_1.JPG?set_id=8800005007</GalleryURL>
     <PhotoDisplay>None</PhotoDisplay>
     <PictureURL>http://i.ebayimg.com/00/s/NzQ4WDEwMjQ=/z/ZhsAAOxyKsZRvrft/$T2eC16dHJHIFFhJTCS+3BRvrftkgS!~~60_1.JPG?set_id=8800005007</PictureURL>
     <PictureURL>http://i.ebayimg.com/00/s/NzQ4WDEwMjQ=/z/QkwAAOxyLchRvrfp/$T2eC16FHJGoFFvohSJ5!BRvrfojwng~~60_1.JPG?set_id=8800005007</PictureURL>
     <PictureURL>http://i.ebayimg.com/00/s/NzQ4WDEwMjQ=/z/x90AAMXQBg5Rvrfr/$(KGrHqVHJFIFG-mN(q46BRvrfrMbOw~~60_1.JPG?set_id=8800005007</PictureURL>
     <PictureURL>http://i.ebayimg.com/00/s/NzQ4WDEwMjQ=/z/8PMAAMXQlgtRvru~/$T2eC16dHJFoE9nh6piThBRvru-6QkQ~~60_1.JPG?set_id=8800005007</PictureURL>
     <PictureURL>http://i.ebayimg.com/00/s/NzQ4WDEwMjQ=/z/0qwAAOxy--NRvrfw/$T2eC16JHJIQE9qUHrVqFBRvrfvzlvw~~60_1.JPG?set_id=8800005007</PictureURL>
     <PictureSource>EPS</PictureSource>
     <GalleryStatus>ImageProcessingError</GalleryStatus>
     <GalleryErrorInfo>Es ist uns nicht möglich, das genaue Problem bei http://i.ebayimg.com/00/s/NzQ4WDEwMjQ=/z/x90AAMXQBg5Rvrfr/$(KGrHqVHJFIFG-mN(q46BRvrfrMbOw~~60_1.JPG?set_id=8800005007 festzustellen. Wenn Sie sich informieren möchten, wie Sie dieses Problem lösen können, gehen Sie bitte zur folgenden eBay-Online-Hilfeseite: http://pages.ebay.de/help/sell/fix_gallery.html</GalleryErrorInfo>
    </PictureDetails>
    <DispatchTimeMax>1</DispatchTimeMax>
    <ProxyItem>false</ProxyItem>
    <BusinessSellerDetails>
     <Address>
      <Street1>Königin-Sophie-Str. 4</Street1>
      <CityName>Bad Honnef</CityName>
      <StateOrProvince>default</StateOrProvince>
      <CountryName>Deutschland</CountryName>
      <Phone>022249886389</Phone>
      <PostalCode>53604</PostalCode>
      <CompanyName>Paydroid UG (haftungsbeschränkt)</CompanyName>
      <FirstName>Ferry</FirstName>
      <LastName>Hötzel</LastName>
     </Address>
     <Fax>022249886379</Fax>
     <Email>info@paydroid.de</Email>
     <TradeRegistrationNumber>HRB 11303</TradeRegistrationNumber>
     <LegalInvoice>true</LegalInvoice>
     <TermsAndConditions>123</TermsAndConditions>
     <VATDetails>
      <VATSite>DE</VATSite>
      <VATID> DE275058598</VATID>
     </VATDetails>
    </BusinessSellerDetails>
    <BuyerGuaranteePrice currencyID="EUR">20000.0</BuyerGuaranteePrice>
    <BuyerRequirementDetails>
     <ShipToRegistrationCountry>true</ShipToRegistrationCountry>
    </BuyerRequirementDetails>
    <ReturnPolicy>
     <ReturnsWithinOption>Days_14</ReturnsWithinOption>
     <ReturnsWithin>14 Tage</ReturnsWithin>
     <ReturnsAcceptedOption>ReturnsAccepted</ReturnsAcceptedOption>
     <ReturnsAccepted>Verbraucher haben das Recht, den Artikel unter den angegebenen Bedingungen zurückzugeben.</ReturnsAccepted>
     <Description></Description>
     <ShippingCostPaidByOption>EUBuyer_CancelRightsUnder40</ShippingCostPaidByOption>
     <ShippingCostPaidBy>Widerrufsrecht: Käufer trägt die regelmäßigen Kosten der Rücksendung, wenn die gelieferte Ware der bestellten entspricht und der Preis der zurückzusendenden Sache 40 Euro nicht übersteigt oder wenn der Käufer bei einem höheren Preis zum Zeitpunkt des Widerrufs noch nicht den Kaufpreis bezahlt oder eine vertraglich vereinbarte Teilzahlung erbracht hat.</ShippingCostPaidBy>
    </ReturnPolicy>
    <ConditionID>1000</ConditionID>
    <ConditionDisplayName>Neu</ConditionDisplayName>
    <PostCheckoutExperienceEnabled>false</PostCheckoutExperienceEnabled>
    <SellerProfiles>
     <SellerShippingProfile>
      <ShippingProfileID>37501926018</ShippingProfileID>
      <ShippingProfileName>Versandbedingungen 99422718</ShippingProfileName>
     </SellerShippingProfile>
     <SellerReturnProfile>
      <ReturnProfileID>49370735018</ReturnProfileID>
      <ReturnProfileName>Rücknahmebedingungen 65666597</ReturnProfileName>
     </SellerReturnProfile>
     <SellerPaymentProfile>
      <PaymentProfileID>37501925018</PaymentProfileID>
      <PaymentProfileName>Zahlungsbedingungen 1</PaymentProfileName>
     </SellerPaymentProfile>
    </SellerProfiles>
    <ShippingPackageDetails>
     <ShippingIrregular>false</ShippingIrregular>
     <ShippingPackage>PackageThickEnvelope</ShippingPackage>
     <WeightMajor measurementSystem="Metric" unit="kg">0</WeightMajor>
     <WeightMinor measurementSystem="Metric" unit="gm">0</WeightMinor>
    </ShippingPackageDetails>
    <HideFromSearch>false</HideFromSearch>
   </Item>
  </GetItemResponse>
 </soapenv:Body>
</soapenv:Envelope>""".format(timestamp=timestamp, signature=signature)


item_suspended_notification_template = lambda timestamp, signature: """<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <soapenv:Header>
    <ebl:RequesterCredentials xmlns:ns="urn:ebay:apis:eBLBaseComponents" xmlns:ebl="urn:ebay:apis:eBLBaseComponents" soapenv:mustUnderstand="0">
       <ebl:NotificationSignature xmlns:ebl="urn:ebay:apis:eBLBaseComponents">{signature}</ebl:NotificationSignature>
    </ebl:RequesterCredentials>
  </soapenv:Header>
  <soapenv:Body>
    <GetItemResponse>
      <Timestamp>{timestamp}</Timestamp>
      <Ack>Success</Ack>
      <CorrelationID>588764920</CorrelationID>
      <Version>859</Version>
      <Build>E859_CORE_API_16653375_R1</Build>
      <NotificationEventName>ItemSuspended</NotificationEventName>
      <RecipientUserID>testuser_inventorum1234</RecipientUserID>
      <EIASToken>nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6wFk4GhCpiGow6dj6x9nY+seQ==</EIASToken>
      <Item>
        <AutoPay>false</AutoPay>
        <BuyerProtection>ItemIneligible</BuyerProtection>
        <BuyItNowPrice currencyID="EUR">0.0</BuyItNowPrice>
        <Country>DE</Country>
        <Currency>EUR</Currency>
        <Description>Über alles</Description>
        <GiftIcon>0</GiftIcon>
        <HitCounter>NoHitCounter</HitCounter>
        <ItemID>110136115192</ItemID>
        <ListingDetails>
          <Adult>false</Adult>
          <BindingAuction>false</BindingAuction>
          <CheckoutEnabled>true</CheckoutEnabled>
          <ConvertedBuyItNowPrice currencyID="EUR">0.0</ConvertedBuyItNowPrice>
          <ConvertedStartPrice currencyID="EUR">148.75</ConvertedStartPrice>
          <ConvertedReservePrice currencyID="EUR">0.0</ConvertedReservePrice>
          <HasReservePrice>false</HasReservePrice>
          <StartTime>2014-02-14T17:01:23.000Z</StartTime>
          <EndTime>2014-02-14T17:06:33.000Z</EndTime>
          <ViewItemURL>http://cgi.sandbox.ebay.de/Happy-Hacking-Professional-2-White-Gray-/110137747643</ViewItemURL>
          <HasUnansweredQuestions>false</HasUnansweredQuestions>
          <HasPublicMessages>false</HasPublicMessages>
          <ViewItemURLForNaturalSearch>http://cgi.sandbox.ebay.de/Happy-Hacking-Professional-2-White-Gray-/110137747643</ViewItemURLForNaturalSearch>
          <EndingReason>NotAvailable</EndingReason>
        </ListingDetails>
        <ListingDesigner>
          <LayoutID>7710000</LayoutID>
          <ThemeID>7710</ThemeID>
        </ListingDesigner>
        <ListingDuration>Days_30</ListingDuration>
        <ListingType>FixedPriceItem</ListingType>
        <Location>Berlin</Location>
        <PaymentMethods>PayPal</PaymentMethods>
        <PayPalEmailAddress>andrea+ebay@inventorum.com</PayPalEmailAddress>
        <PrimaryCategory>
          <CategoryID>11872</CategoryID>
          <CategoryName>Beauty &amp; Gesundheit:Maniküre &amp; Pediküre:Instrumente, Sets &amp; Zubehör</CategoryName>
        </PrimaryCategory>
        <PrivateListing>false</PrivateListing>
        <Quantity>5</Quantity>
        <ReservePrice currencyID="EUR">0.0</ReservePrice>
        <ReviseStatus>
          <ItemRevised>false</ItemRevised>
        </ReviseStatus>
        <Seller>
          <AboutMePage>false</AboutMePage>
          <Email>michal@inventorum.com</Email>
          <FeedbackScore>500</FeedbackScore>
          <PositiveFeedbackPercent>0.0</PositiveFeedbackPercent>
          <FeedbackPrivate>false</FeedbackPrivate>
          <FeedbackRatingStar>Purple</FeedbackRatingStar>
          <IDVerified>true</IDVerified>
          <eBayGoodStanding>true</eBayGoodStanding>
          <NewUser>false</NewUser>
          <RegistrationDate>1995-01-01T00:00:00.000Z</RegistrationDate>
          <Site>Germany</Site>
          <Status>Confirmed</Status>
          <UserID>testuser_inventorum1234</UserID>
          <UserIDChanged>false</UserIDChanged>
          <UserIDLastChanged>2013-08-28T15:17:57.000Z</UserIDLastChanged>
          <VATStatus>VATTax</VATStatus>
          <SellerInfo>
            <AllowPaymentEdit>true</AllowPaymentEdit>
            <CheckoutEnabled>true</CheckoutEnabled>
            <CIPBankAccountStored>false</CIPBankAccountStored>
            <GoodStanding>true</GoodStanding>
            <LiveAuctionAuthorized>false</LiveAuctionAuthorized>
            <MerchandizingPref>OptIn</MerchandizingPref>
            <QualifiesForB2BVAT>false</QualifiesForB2BVAT>
            <StoreOwner>false</StoreOwner>
            <SafePaymentExempt>true</SafePaymentExempt>
          </SellerInfo>
          <MotorsDealer>false</MotorsDealer>
        </Seller>
        <SellingStatus>
          <BidCount>0</BidCount>
          <BidIncrement currencyID="EUR">0.0</BidIncrement>
          <ConvertedCurrentPrice currencyID="EUR">148.75</ConvertedCurrentPrice>
          <CurrentPrice currencyID="EUR">148.75</CurrentPrice>
          <LeadCount>0</LeadCount>
          <MinimumToBid currencyID="EUR">148.75</MinimumToBid>
          <QuantitySold>0</QuantitySold>
          <ReserveMet>true</ReserveMet>
          <SecondChanceEligible>false</SecondChanceEligible>
          <ListingStatus>Completed</ListingStatus>
          <QuantitySoldByPickupInStore>0</QuantitySoldByPickupInStore>
        </SellingStatus>
        <ShippingDetails>
          <ApplyShippingDiscount>false</ApplyShippingDiscount>
          <CalculatedShippingRate>
            <WeightMajor measurementSystem="Metric" unit="kg">0</WeightMajor>
            <WeightMinor measurementSystem="Metric" unit="gm">0</WeightMinor>
          </CalculatedShippingRate>
          <InsuranceFee currencyID="EUR">0.0</InsuranceFee>
          <InsuranceOption>NotOffered</InsuranceOption>
          <SalesTax>
            <SalesTaxPercent>0.0</SalesTaxPercent>
            <ShippingIncludedInTax>false</ShippingIncludedInTax>
          </SalesTax>
          <ShippingServiceOptions>
            <ShippingService>DE_DHLPaket</ShippingService>
            <ShippingServiceCost currencyID="EUR">5.0</ShippingServiceCost>
            <ShippingServiceAdditionalCost currencyID="EUR">2.0</ShippingServiceAdditionalCost>
            <ShippingServicePriority>1</ShippingServicePriority>
            <ExpeditedService>false</ExpeditedService>
            <ShippingTimeMin>1</ShippingTimeMin>
            <ShippingTimeMax>2</ShippingTimeMax>
          </ShippingServiceOptions>
          <ShippingType>Flat</ShippingType>
          <ThirdPartyCheckout>false</ThirdPartyCheckout>
          <InsuranceDetails>
            <InsuranceOption>NotOffered</InsuranceOption>
          </InsuranceDetails>
          <ShippingDiscountProfileID>0</ShippingDiscountProfileID>
          <InternationalShippingDiscountProfileID>0</InternationalShippingDiscountProfileID>
          <SellerExcludeShipToLocationsPreference>true</SellerExcludeShipToLocationsPreference>
        </ShippingDetails>
        <ShipToLocations>DE</ShipToLocations>
        <Site>Germany</Site>
        <StartPrice currencyID="EUR">148.75</StartPrice>
        <TimeLeft>PT0S</TimeLeft>
        <Title>Happy Hacking Professional 2 (White/Gray) Über</Title>
        <HitCount>0</HitCount>
        <LocationDefaulted>true</LocationDefaulted>
        <GetItFast>false</GetItFast>
        <PostalCode>10555</PostalCode>
        <PictureDetails>
          <PhotoDisplay>None</PhotoDisplay>
        </PictureDetails>
        <DispatchTimeMax>3</DispatchTimeMax>
        <ProxyItem>false</ProxyItem>
        <BuyerGuaranteePrice currencyID="EUR">20000.0</BuyerGuaranteePrice>
        <ReturnPolicy>
          <ReturnsWithinOption>Days_14</ReturnsWithinOption>
          <ReturnsWithin>14 Tage</ReturnsWithin>
          <ReturnsAcceptedOption>ReturnsAccepted</ReturnsAcceptedOption>
          <ReturnsAccepted>Verbraucher haben das Recht, den Artikel unter den angegebenen Bedingungen zurückzugeben.</ReturnsAccepted>
          <ShippingCostPaidByOption>EUBuyer_CancelRightsUnder40</ShippingCostPaidByOption>
          <ShippingCostPaidBy>Widerrufsrecht: Käufer trägt die regelmäßigen Kosten der Rücksendung, wenn die gelieferte Ware der bestellten entspricht und der Preis der zurückzusendenden Sache 40 Euro nicht übersteigt oder wenn der Käufer bei einem höheren Preis zum Zeitpunkt des Widerrufs noch nicht den Kaufpreis bezahlt oder eine vertraglich vereinbarte Teilzahlung erbracht hat.</ShippingCostPaidBy>
        </ReturnPolicy>
        <PaymentAllowedSite>Germany</PaymentAllowedSite>
        <ConditionID>1000</ConditionID>
        <ConditionDisplayName>Neu</ConditionDisplayName>
        <PostCheckoutExperienceEnabled>false</PostCheckoutExperienceEnabled>
        <ShippingPackageDetails>
          <ShippingIrregular>false</ShippingIrregular>
          <ShippingPackage>None</ShippingPackage>
          <WeightMajor measurementSystem="Metric" unit="kg">0</WeightMajor>
          <WeightMinor measurementSystem="Metric" unit="gm">0</WeightMinor>
        </ShippingPackageDetails>
        <HideFromSearch>false</HideFromSearch>
      </Item>
    </GetItemResponse>
  </soapenv:Body>
</soapenv:Envelope>""".format(timestamp=timestamp, signature=signature)
